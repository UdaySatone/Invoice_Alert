import streamlit as st
from gemini_logic import analyze_document
import pdfplumber
import requests
from dotenv import load_dotenv
import os
load_dotenv()
webhook_url = os.getenv("N8N_WEBHOOK_URL")

st.set_page_config(page_title="AI Document Orchestrator", layout="centered")
st.title("AI-Powered Invoice Orchestrator")

uploaded_file = st.file_uploader("Upload your document (PDF or Text)", type=["pdf", "txt"])
question = st.text_input("Ask a question about the document")

document_text = None

if uploaded_file:
    if uploaded_file.type == "text/plain":
        document_text = uploaded_file.read().decode("utf-8")
        st.success("TXT file read successfully")

    elif uploaded_file.type == "application/pdf":
        with pdfplumber.open(uploaded_file) as pdf:
            pages = []
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    pages.append(text)

            document_text = "\n".join(pages)

        st.success("PDF file read successfully")

    if not document_text.strip():
        st.warning("No readable text found in Text\PDF")
        st.stop()

if document_text and question:
    with st.spinner("Analyzing document..."):
        try:
            result = analyze_document(document_text, question)
        except Exception as e:
            st.error("AI analysis failed. Please try again.")
            st.stop()

    st.subheader("AI Analysis Result")
    st.write(result["final_answer"])
    risk_level = result["structured_data"]["risk_assessment"]["risk_level"]
    risk_reason = result["structured_data"]["risk_assessment"]["risk_reason"]
    st.subheader("Risk Assessment")
    if risk_level == "HIGH":
        st.error("HIGH RISK INVOICE DETECTED")
        st.write(f"Reason: {risk_reason}")
        st.info("This document requires immediate managerial review.")
        if st.button("Send Alert to Manager"):
            payload = {
                "recipient_email": "udaysatone3@gmail.com",
                "risk_level": risk_level,
                "risk_reason": risk_reason,
                "structured_data": result["structured_data"],
                "final_answer": result["final_answer"]
            }

            try:
                response = requests.post(
                    webhook_url,
                    json=payload,
                    timeout=10
                )

                if response.status_code == 200:
                    st.success("Manager alert sent successfully")
                    st.json(response.json())
                else:
                    st.error("n8n responded with an error")

            except Exception as e:
                st.error("Failed to connect to automation service")

    elif risk_level == "MEDIUM":
        st.warning("MEDIUM RISK INVOICE")
        st.write(f"Reason: {risk_reason}")
        st.info("Manual review is recommended.")

    elif risk_level == "LOW":
        st.success("LOW RISK INVOICE")
        st.write("No managerial action required.")

    else:
        st.warning("Risk level could not be determined.")