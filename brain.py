import os
import streamlit as st
import time
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
    system_prompt = (
        f"You are an Industrial PLC Expert for {brand}. "
        "Generate ONLY Structured Text code. No administrative footers. "
        "Requirements:\n"
        "1. Identify specific devices from user prompt.\n"
        "2. Use 'VAR...END_VAR' for all declarations.\n"
        "3. Always wrap logic in an 'IF E_STOP = FALSE' safety block.\n"
        "4. Use Blink/Cycle logic if 'every X seconds' is mentioned."
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
    Act as a Technical Writer. Create a professional Technical Manual for: {generated_code}.
    Headers Required:
    1. System Overview
    2. Functional Description
    3. Safety & Interlocks
    4. I/O Mapping
    5. Troubleshooting & Maintenance
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

def simulate_logic(input_state, estop_state, start_time, has_timer):
    output_state = False
    elapsed_in_cycle = 0
    if not estop_state and input_state:
        if has_timer:
            total_elapsed = time.time() - start_time
            cycle_time = 10.0 # 5s ON + 5s OFF
            elapsed_in_cycle = total_elapsed % cycle_time
            # Output is ON (True) during the first 5 seconds
            output_state = True if elapsed_in_cycle < 5.0 else False
        else:
            output_state = True
    return output_state, elapsed_in_cycle

def convert_to_pdf(markdown_text):
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