import streamlit as st
from main import fetch_case_details_by_cnr
import json

st.set_page_config(page_title="CNR Case Lookup", layout="centered")

st.title("🔍 CNR Number Case Lookup")
st.markdown("""
Enter a valid **CNR Number** (e.g., `GJAH240000792025`) to fetch case details from the Indian eCourts system.

> ⚠️ **Disclaimer:** The CAPTCHA matching process may occasionally fail due to recognition errors. If case details are not fetched correctly, please try again.
""")

cnr_number = st.text_input("🔢 Enter CNR Number")

if st.button("📂 Fetch Case Details"):
    if cnr_number:
        with st.spinner("Fetching case details... Please wait."):
            case_details = fetch_case_details_by_cnr(cnr_number)
        
        if case_details:
            st.success("✅ Case details fetched successfully!")

            # Tabs for organizing different sections
            tabs = st.tabs(["📄 Overview", "📌 Case Status", "👥 Parties", "⚖️ Acts", "📚 History", "📁 JSON"])

            with tabs[0]:
                st.subheader("📄 Case Details")
                for key, val in case_details.get("Case Details", {}).items():
                    st.write(f"**{key}:** {val}")

            with tabs[1]:
                st.subheader("📌 Case Status")
                for key, val in case_details.get("Case Status", {}).items():
                    st.write(f"**{key}:** {val}")

            with tabs[2]:
                st.subheader("👥 Parties")
                st.write("**Petitioner & Advocate:**")
                st.write(case_details.get("Petitioner and Advocate", "Not available"))
                st.write("**Respondent & Advocate:**")
                st.write(case_details.get("Respondent and Advocate", "Not available"))

            with tabs[3]:
                st.subheader("⚖️ Acts Involved")
                for key, val in case_details.get("Acts", {}).items():
                    st.write(f"**{key}:** {val}")

            with tabs[4]:
                st.subheader("📚 Case History")
                history = case_details.get("Case History", [])
                if history:
                    for i, entry in enumerate(history, 1):
                        st.markdown(f"**{i}.** {entry['Hearing Date']} - {entry['Purpose of Hearing']} (Judge: {entry['Judge']})")
                else:
                    st.write("No case history found.")

            with tabs[5]:
                st.subheader("📁 Raw JSON Output")
                st.json(case_details)
                st.download_button("📥 Download JSON", data=json.dumps(case_details, indent=4), file_name="case_details.json")

        else:
            st.error("❌ Could not fetch case details. Please check the CNR number or try again later.")
    else:
        st.warning("⚠️ Please enter a valid CNR number.")
