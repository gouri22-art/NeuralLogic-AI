import os
import streamlit as st
from groq import Groq
from dotenv import load_dotenv

# 1. Load local .env if it exists (for local development)
load_dotenv()

def get_groq_client():
    """
    Safely retrieves the API key and initializes the Groq client.
    """
    # Checks Streamlit Cloud Secrets first, then local .env
    api_key = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")
    
    if not api_key:
        st.error("Missing Groq API Key! Please add it to your Secrets or .env file.")
        st.stop()
        
    return Groq(api_key=api_key)

def generate_plc_code(user_instruction):
    """
    Sends natural language to Groq and returns PLC Structured Text.
    """
    client = get_groq_client()
    
    # This 'System Prompt' is the "Rules of the Game" for the AI
    system_prompt = (
        "You are an expert Senior Automation Engineer. "
        "Convert the user's English instructions into professional IEC 61131-3 Structured Text (ST). "
        "Strict Rules: "
        "1. Start with a VAR...END_VAR block defining all inputs, outputs, and timers. "
        "2. Use clear, descriptive variable names (e.g., Motor_Start, Temp_Sensor). "
        "3. Every output MUST be disabled if 'E_STOP' (Emergency Stop) is TRUE. "
        "4. Add comments using (* comment *) for each section. "
        "5. Provide ONLY the code. Do not include introductory text or explanations."
    )

    try:
        # llama-3.3-70b-versatile is excellent for coding tasks
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Convert this to PLC ST: {user_instruction}"}
            ],
            temperature=0.1,  # Keep temperature low for precise, non-creative code
            max_tokens=1024
        )
        
        return completion.choices[0].message.content

    except Exception as e:
        return f"⚠️ Groq API Error: {str(e)}"