# utils/email_verifier.py
import re
import smtplib
import dns.resolver
import socket
import time
import random

EMAIL_REGEX = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")

def verify_email(email, helo_domain="sendgrid.com", mail_from="support@sendgrid.com"):
    result = {
        "valid": False,
        "smtp_code": None,
        "smtp_message": "",
        "catch_all": False,
        "error": ""
    }
    if not EMAIL_REGEX.match(email):
        result["error"] = f"Invalid email format: {email}"
        return result
    try:
        domain = email.split('@')[-1]
        # Get MX records
        try:
            mx_records = dns.resolver.resolve(domain, 'MX')
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
            result["error"] = f"No MX record found for domain: {domain}"
            return result
        mx_host = str(mx_records[0].exchange).rstrip('.')
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
                            result.update({
                                "valid": True,
                                "smtp_code": verify_code,
                                "smtp_message": str(verify_message)
                            })
                            break
                    except Exception:
                        pass  # Not all servers support VRFY
                    code, message = server.rcpt(email)
                    result["smtp_code"] = code
                    result["smtp_message"] = str(message)
                    if code == 421 or (isinstance(message, bytes) and b'421' in message):
                        delay = random.uniform(2, 5)
                        time.sleep(delay)
                        continue
                    result["valid"] = code in [250, 251]
                    break
            except smtplib.SMTPResponseException as e:
                if e.smtp_code == 421:
                    delay = random.uniform(2, 5)
                    time.sleep(delay)
                    continue
                else:
                    result["error"] = f"SMTP error: {e.smtp_error}"
                    break
            except Exception as e:
                result["error"] = f"Unexpected error: {e}"
                break
        # Catch-all check: try a random address at the domain
        try:
            random_local = f"catchalltest{random.randint(10000,99999)}"
            random_email = f"{random_local}@{domain}"
            with smtplib.SMTP(timeout=10) as server:
                server.connect(mx_host, 25)
                server.helo(helo_domain)
                server.mail(mail_from)
                code, message = server.rcpt(random_email)
                if code in [250, 251]:
                    result["catch_all"] = True
        except Exception:
            pass  # If catch-all check fails, ignore
        return result
    except (socket.gaierror, smtplib.SMTPConnectError) as e:
        result["error"] = f"SMTP connection error: {e}"
        return result
    except Exception as e:
        result["error"] = f"Unexpected error: {e}"
        return result