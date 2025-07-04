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
        # Handle both dict and boolean (True/False) results
        if isinstance(result, dict):
            if result.get("deliverable"):
                st.success(f"{email} is valid! Score: {result.get('score', 'N/A')}")
            else:
                st.error(f"{email} is invalid or unverifiable. Score: {result.get('score', 'N/A')}")
            st.write("**EHLO Success:**", result.get("ehlo", "N/A"))
            st.write("**HELO Success:**", result.get("helo", "N/A"))
            st.write("**Deliverable:**", result.get("deliverable", "N/A"))
            if result.get("error"):
                st.warning(f"Error: {result['error']}")
        else:
            if result:
                st.success(f"{email} is valid!")
            else:
                st.error(f"{email} is invalid or unverifiable.")

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
                if isinstance(res, dict):
                    results.append({
                        "Email": email,
                        "Score": res.get("score", "N/A"),
                        "EHLO": res.get("ehlo", "N/A"),
                        "HELO": res.get("helo", "N/A"),
                        "Deliverable": res.get("deliverable", "N/A"),
                        "Error": res.get("error", "")
                    })
                else:
                    results.append({
                        "Email": email,
                        "Score": "N/A",
                        "EHLO": "N/A",
                        "HELO": "N/A",
                        "Deliverable": res,
                        "Error": ""
                    })
        result_df = pd.DataFrame(results)
        st.dataframe(result_df)
        # Download link using in-memory buffer
        output = io.BytesIO()
        result_df.to_excel(output, index=False)
        output.seek(0)
        st.download_button(
            label="⬇️ Download Results as Excel",
            data=output,
            file_name="verified_results.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
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
                valid = verify_email(email)
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
