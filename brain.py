import os
import streamlit as st
from groq import Groq
from dotenv import load_dotenv
from markdown_pdf import MarkdownPdf, Section
from io import BytesIO
from md2docx_python.src.md2docx_python import markdown_to_word
import tempfile

load_dotenv()

def get_groq_client():
    api_key = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")
    if not api_key:
        st.error("Missing Groq API Key!")
        st.stop()
    return Groq(api_key=api_key)

def generate_plc_code(user_instruction, brand):
    client = get_groq_client()
    # Forces structure like: VAR -> Variables -> END_VAR -> IF E_STOP = FALSE
    system_prompt = (
        f"You are a Senior PLC Developer for {brand}. "
        "Task: Generate ONLY Structured Text. No conversational text. No 'Approved by'. "
        "Required Format:\n"
        "VAR\n"
        "  Sensor_B : BOOL;\n"
        "  Motor_Start : BOOL;\n"
        "  E_STOP : BOOL;\n"
        "END_VAR\n\n"
        "IF E_STOP = FALSE THEN\n"
        "  IF [Logic] THEN\n"
        "    [Action];\n"
        "  ELSE\n"
        "    [Action];\n"
        "  END_IF;\n"
        "END_IF;"
    )
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": system_prompt},
                      {"role": "user", "content": f"Logic Request: {user_instruction}"}],
            temperature=0.1
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

def generate_documentation(generated_code, brand):
    client = get_groq_client()
    doc_prompt = f"""
    Act as a Technical Writer. Create a professional Technical Manual for this {brand} PLC code.
    DO NOT include 'Approved by', 'Date', or 'Engineer Name' fields.
    
    Required Sections:
    1. System Overview
    2. Functional Description
    3. Safety and Interlocks
    4. IO Mapping
    5. Troubleshooting
    """
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": doc_prompt}],
            temperature=0.3
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

def convert_to_pdf(markdown_text):
    # FIXED: toc_level=0 prevents link errors in PyMuPDF
    pdf = MarkdownPdf(toc_level=0) 
    pdf.add_section(Section(markdown_text))
    pdf_buffer = BytesIO()
    pdf.save_bytes(pdf_buffer)
    return pdf_buffer.getvalue()

def convert_to_word(markdown_text):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp_word:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".md", mode='w', encoding='utf-8') as tmp_md:
            tmp_md.write(markdown_text)
            tmp_md_path = tmp_md.name
        markdown_to_word(tmp_md_path, tmp_word.name)
        with open(tmp_word.name, "rb") as f:
            word_data = f.read()
    return word_data