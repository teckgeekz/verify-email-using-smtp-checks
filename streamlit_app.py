import streamlit as st
import pandas as pd
from utils.email_verifier import verify_email
import tempfile
import os
import io
import random
import time
from utils.linkedin_scraper import find_linkedin_profile
from utils.email_guesser import guess_emails

st.set_page_config(page_title="Email Verifier", layout="centered")
st.title("📧 Email Verifier (Streamlit)")

option = st.sidebar.radio("Choose Mode", ("Single Email", "Bulk Verify", "Lead Contact Finder"))

with st.sidebar:
    st.markdown("### 🚀 Lead For Sure")
    st.markdown("✅ **100% Accuracy (for supported domains)**")
    st.markdown("🆓 **Find & verify up to 1000 emails (free)**")

def single_email_mode():
    st.header("Single Email Verification")
    email = st.text_input("Enter email address:")
    if st.button("Verify"):
        with st.spinner("Verifying..."):
            result = verify_email(email)
        # Handle dict result from current email_verifier.py
        if result["valid"]:
            st.success(f"{email} is valid!")
        else:
            st.error(f"{email} is invalid or unverifiable. {result.get('error', '')}")

def bulk_verify_mode():
    st.header("Bulk Email Verification")
    uploaded_file = st.file_uploader("Upload CSV or Excel file with an 'Email' column", type=["csv", "xlsx"])
    if uploaded_file:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        if "Email" not in df.columns:
            st.error("Missing required column: 'Email'")
            return
        results = []
        with st.spinner("Verifying emails..."):
            for email in df["Email"]:
                email = str(email).strip()
                res = verify_email(email)
                # Handle dict result from current email_verifier.py
                results.append({
                    "Email": email,
                    "Valid": "✅ Valid" if res["valid"] else "❌ Invalid",
                    "Status": res["valid"]
                })
        result_df = pd.DataFrame(results)
        st.dataframe(result_df)
        # Download link using CSV format (more reliable)
        csv_data = result_df.to_csv(index=False)
        st.download_button(
            label="⬇️ Download Results as CSV",
            data=csv_data,
            file_name="verified_results.csv",
            mime="text/csv"
        )

def lead_contact_finder_mode():
    st.header("Lead Contact Finder")
    name = st.text_input("Full Name:")
    company = st.text_input("Company Name:")
    domain = st.text_input("Domain (example.com):")
    if st.button("Find Lead Contact"):
        with st.spinner("Searching and verifying..."):
            linkedin_url, title = find_linkedin_profile(name, company)
            emails = guess_emails(name, domain)
            verified_emails = []
            found = False
            for email in emails:
                valid = verify_email(email)["valid"]
                verified_emails.append((email, valid))
                if valid:
                    found = True
                    break
                delay = random.uniform(2, 5)
                st.info(f"Sleeping for {delay:.2f} seconds before next verification...")
                time.sleep(delay)
        st.subheader("Result:")
        st.write(f"**Name:** {name}")
        st.write(f"**Company:** {company}")
        st.write(f"**Title:** {title or 'N/A'}")
        st.write(f"**LinkedIn:** [{linkedin_url}]({linkedin_url})" if linkedin_url else "**LinkedIn:** N/A")
        st.write("**Emails:**")
        for email, valid in verified_emails:
            st.write(f"{email} - {'✅ Valid' if valid else '❌ Invalid'}")

if option == "Single Email":
    single_email_mode()
elif option == "Bulk Verify":
    bulk_verify_mode()
else:
    lead_contact_finder_mode()
