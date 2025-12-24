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
    """Handles API key retrieval from Streamlit Secrets or Local .env"""
    api_key = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")
    if not api_key:
        st.error("Missing Groq API Key! Please check your secrets.toml or .env file.")
        st.stop()
    return Groq(api_key=api_key)

def generate_plc_code(user_instruction, brand):
    """Generates the actual Structured Text code."""
    client = get_groq_client()
    
    system_prompt = (
        f"You are a Senior Automation Engineer specializing in {brand}. "
        "Convert instructions into professional IEC 61131-3 Structured Text. "
        "1. Every 'IF' MUST have a corresponding 'END_IF;'. "
        "2. Include a VAR...END_VAR block with descriptive tags. "
        "3. Ensure an E_STOP safety interlock is present. "
        "4. Provide ONLY the code block. No conversational chatter."
    )

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Hardware: {brand}. Logic: {user_instruction}"}
            ],
            temperature=0.1
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error Generating Code: {str(e)}"

def generate_documentation(generated_code, brand):
    """Generates the Maintenance Manual based on the generated code."""
    client = get_groq_client()
    
    doc_prompt = f"""
    You are a Technical Writer for Industrial Automation. 
    Below is PLC code for {brand}. Write a professional 'Functional Description'.
    
    Include:
    1. **Operational Overview**: What does this logic do?
    2. **Sequence of Operations**: Step-by-step signal flow.
    3. **Troubleshooting**: 3 common reasons why this might fault.
    
    CODE:
    {generated_code}
    """

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": doc_prompt}],
            temperature=0.3
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error Generating Documentation: {str(e)}"

def convert_to_pdf(markdown_text):
    pdf = MarkdownPdf(toc_level=2)
    pdf.add_section(Section(markdown_text))
    pdf_buffer = BytesIO()
    pdf.save_bytes(pdf_buffer)
    return pdf_buffer.getvalue()

def convert_to_word(markdown_text):
    # Word conversion requires a temporary file because md2docx writes to disk
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp_word:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".md", mode='w', encoding='utf-8') as tmp_md:
            tmp_md.write(markdown_text)
            tmp_md_path = tmp_md.name
        
        markdown_to_word(tmp_md_path, tmp_word.name)
        with open(tmp_word.name, "rb") as f:
            word_data = f.read()
    return word_data