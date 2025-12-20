import os
import streamlit as st
from groq import Groq
from dotenv import load_dotenv

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
        return f"Error: {str(e)}"