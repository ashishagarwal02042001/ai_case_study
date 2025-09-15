import streamlit as st
import requests
import os
import datetime as dt
import pandas as pd

# Backend URL
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

def prepare_files_payload(files):
    for f in files:
        f.seek(0)
    return [("files", (f.name, f, f.type)) for f in files]


st.set_page_config(page_title="Social Support Application Portal", layout="wide")
st.title("Social Support Application Portal")

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Applicant Form", "Chatbot"])

if page == "Applicant Form":
    st.header("Submit Your Application")

    uploaded_files = st.file_uploader(
        "Upload all required documents (Bank Statement, Emirates ID, Resume, Credit Report, Assets/Liabilities)",
        accept_multiple_files=True
    )

    if uploaded_files:
        files_payload = [("files", (f.name, f, f.type)) for f in uploaded_files]
        try:
            resp = requests.post(f"{BACKEND_URL}/extract", files=files_payload)
            if resp.status_code == 200:
                extracted = resp.json()
                st.success("Extracted information from documents")

                with st.form("review_form"):
                    name = st.text_input("Full Name", value=extracted["fields"].get("name", ""))
                    dob_str = extracted["fields"].get("dob")
                    default_dob = dt.date(1990, 1, 1)
                    try:
                        if dob_str:
                            default_dob = dt.datetime.strptime(dob_str.split("T")[0], "%Y-%m-%d").date()
                    except Exception:
                        pass
                    dob = st.date_input(
                        "Date of Birth",
                        value=default_dob,
                        min_value=dt.date(1900, 1, 1),
                        max_value=dt.date.today()
                    )
                    address = st.text_area("Address", value=extracted["fields"].get("address", ""))
                    family_size = st.number_input(
                        "Family Size",
                        min_value=1,
                        step=1,
                        value=int(extracted["fields"].get("family_size", 1))
                    )
                    income = st.number_input(
                        "Monthly Income (AED)",
                        min_value=0,
                        value=int(extracted["fields"].get("reported_income", 0))
                    )
                    confirmed = st.form_submit_button("Submit Application")
                    if confirmed:
                        data_payload = {
                            "name": name,
                            "dob": str(dob),
                            "address": address,
                            "family_size": family_size,
                            "income": income
                        }
                        files_payload_predict = prepare_files_payload(uploaded_files)
                        # print(files_payload_predict)
                        resp2 = requests.post(f"{BACKEND_URL}/predict", data=data_payload, files=files_payload_predict)
                        # print(resp2.json())
                        if resp2.status_code == 200:
                            st.success("Application submitted successfully")
                            st.json(resp2.json())
                        else:
                            st.error(f"Error: {resp2.text}")
            else:
                st.error(f"Extraction failed: {resp.text}")
        except Exception as e:
            st.error(f"Failed to connect to backend: {e}")

elif page == "Chatbot":
    st.header("Ask the AI Assistant")
    query = st.text_input("Type your question about your application:")
    app_id = st.text_input("Application ID (optional)", "")

    if st.button("Ask"):
        if not query.strip():
            st.warning("Please enter a question.")
        else:
            try:
                resp = requests.post(f"{BACKEND_URL}/explain", json={"query": query, "app_id": app_id})
                if resp.status_code == 200:
                    st.write(resp.json().get("answer", "No response"))
                else:
                    st.error(f"Chatbot error: {resp.text}")
            except Exception as e:
                st.error(f"Failed to reach backend: {e}")