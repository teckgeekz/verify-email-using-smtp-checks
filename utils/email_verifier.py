# utils/email_verifier.py
import re
import smtplib
import dns.resolver
import socket
import time
import random

EMAIL_REGEX = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")

def verify_email(email, helo_domain="apollo.io", mail_from="support@apollo.io"):
    # Check email format first
    if not EMAIL_REGEX.match(email):
        print(f"❌ Invalid email format: {email}")
        return False
    try:
        domain = email.split('@')[-1]
        # Get MX records
        mx_records = dns.resolver.resolve(domain, 'MX')
        mx_host = str(mx_records[0].exchange).rstrip('.')
        print(f"✅ MX record found for {domain}: {mx_host}")
        max_retries = 2
        for attempt in range(max_retries):
            try:
                with smtplib.SMTP(timeout=10) as server:
                    server.connect(mx_host, 25)
                    server.helo(helo_domain)
                    server.mail(mail_from)
                    # Try verify first (may not be supported)
                    try:
                        verify_code, verify_message = server.verify(email)
                        if verify_code in [250, 251]:
                            return True
                    except Exception:
                        pass  # Not all servers support VRFY
                    code, message = server.rcpt(email)
                    if code == 421 or (isinstance(message, bytes) and b'421' in message):
                        print(f"❌ 421 error: {message}. Retrying after delay...")
                        delay = random.uniform(2, 5)
                        print(f"Sleeping for {delay:.2f} seconds before retry...")
                        time.sleep(delay)
                        continue
                    return code in [250, 251]  # 250 is accepted, 251 is "will forward"
            except smtplib.SMTPResponseException as e:
                if e.smtp_code == 421:
                    print(f"❌ 421 error: {e.smtp_error}. Retrying after delay...")
                    delay = random.uniform(2, 5)
                    print(f"Sleeping for {delay:.2f} seconds before retry...")
                    time.sleep(delay)
                    continue
                else:
                    print(f"❌ SMTP error: {e.smtp_error}")
                    return False
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                return False
        return False
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
        print(f"❌ No MX record found for domain: {domain}")
        return False
    except (socket.gaierror, smtplib.SMTPConnectError) as e:
        print(f"❌ SMTP connection error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False