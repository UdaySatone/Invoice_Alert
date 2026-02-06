from google import genai
import json
import re
from dotenv import load_dotenv
import os
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)

def analyze_document(document_text, question):
    prompt = """
    You are an AI document analyst.
    
    Tasks:
    1. Identify the document type.
    2. Extract key structured data required to analyze the document.
    3. Assess financial risk.
    4. Answer the user's question clearly and concisely.
    
    Return ONLY valid JSON matching this schema:
    
    {
    "structured_data": {
    "document_type": "",
    "key_facts": {
    "vendor_name": "",
    "invoice_amount": null,
    "invoice_date": "",
    "due_date": "",
    "payment_terms": ""
    },
    "risk_assessment": {
    "risk_level": "",
    "risk_reason": ""
    }
    },
    "final_answer": ""
    }
    Risk rules:
    - If invoice_amount > 10000 → HIGH
    - If invoice_amount between 5001 and 10000 → MEDIUM
    - If invoice_amount <= 5000 → LOW
    - If invoice_amount is null → HIGH
    
    Rules:
    - If a field is missing, return an empty string (or null for invoice_amount).
    - Do not include explanations outside JSON.
    - Do not include markdown or code fences.
    
    Document:
    <<<DOCUMENT_TEXT>>>
    User Question:
    <<<USER_QUESTION>>>
    """

    response = client.models.generate_content(
        model="models/gemini-2.5-flash",
        contents= prompt.replace("<<<DOCUMENT_TEXT>>>", document_text).replace("<<<USER_QUESTION>>>", question)
    )

    raw_output = response.text
    match = re.search(r"\{.*\}", raw_output, re.DOTALL)
    if not match:
        raise ValueError("No JSON found")

    return json.loads(match.group(0))