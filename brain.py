import os
import streamlit as st
from groq import Groq
from markdown_pdf import MarkdownPdf, Section
from io import BytesIO
import tempfile
import re
from md2docx_python.src.md2docx_python import markdown_to_word
import time

def get_client():
    """Initializes the Groq client using secrets or environment variables."""
    api_key = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")
    if not api_key:
        st.error("GROQ_API_KEY not found. Please check your Streamlit secrets.")
    return Groq(api_key=api_key)

def generate_plc_code(user_instruction, brand):
    """Generates Structured Text, Ladder, and XML sections via LLM."""
    client = get_client()
    system_prompt = (
        f"You are a Senior Automation Engineer specialized in {brand}. "
        "Output code in three distinct sections: "
        "1. Structured Text (IEC 61131-3). "
        "2. ---LADDER_START--- followed by ASCII representation. "
        "3. ---XML_START--- followed by PLCopen XML."
    )
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_instruction}],
        temperature=0.1
    )
    return completion.choices[0].message.content

def generate_documentation(code, brand):
    """Generates a comprehensive Technical Manual for the generated code."""
    client = get_client()
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "user", "content": f"Create a professional Technical Manual for this {brand} PLC code. Include sections for Overview, I/O Mapping, and Operational Logic:\n{code}"}
        ]
    )
    return completion.choices[0].message.content

def generate_xml_extension(st_code, tags):
    """Creates a basic PLCopen XML structure for hardware import."""
    vars_xml = "".join([f'<variable name="{t[0]}"><type><{t[1]}/></type></variable>' for t in tags])
    xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://www.plcopen.org/xml/tc6_0201">
  <types>
    <pous>
      <pou name="NeuralLogic_Main" pouType="program">
        <interface><localVars>{vars_xml}</localVars></interface>
        <body><ST><xhtml xmlns="http://www.w3.org/1999/xhtml">{st_code}</xhtml></ST></body>
      </pou>
    </pous>
  </types>
</project>"""
    return xml_content

def simulate_logic(inputs, estop, master_start, current_speed=0):
    """
    Simulates Industrial Physics with Acceleration (Ramp Up).
    Handles the speed transition from 0 to 1750 RPM.
    """
    state = {
        "active": False,
        "speed": current_speed,
        "load": 0.0,
        "health": 100,
        "message": "System Ready",
        "color": "#94a3b8" 
    }

    # 1. SAFETY & INTERLOCKS
    if estop:
        state.update({"speed": 0, "message": "🚨 EMERGENCY STOP ACTIVE", "color": "#ef4444"})
        return state, 0
    
    if not master_start:
        state.update({"speed": 0, "message": "⚪ STANDBY: Master Start Off", "color": "#64748b"})
        return state, 0

    # 2. KEYWORD-BASED TAG DETECTION
    start_signal = any(v for k, v in inputs.items() if any(x in k.upper() for x in ["START", "RUN", "MOTOR"]))
    sensor_signal = any(v for k, v in inputs.items() if any(x in k.upper() for x in ["SENSOR", "PROX", "SWITCH"]))
    requires_sensor = any("SENSOR" in k.upper() for k in inputs.keys())

    # 3. RAMP-UP LOGIC (The Physics Engine)
    target_speed = 1750 if (start_signal and (not requires_sensor or sensor_signal)) else 0
    accel_rate = 150 # Increase per screen refresh
    
    if state["speed"] < target_speed:
        state["speed"] = min(state["speed"] + accel_rate, target_speed)
    elif state["speed"] > target_speed:
        state["speed"] = max(state["speed"] - accel_rate, 0)

    # 4. FINAL STATE CALCULATION
    if state["speed"] > 0:
        jitter = (int(time.time() * 10) % 10)
        is_at_target = (state["speed"] == target_speed)
        
        state.update({
            "active": True,
            "speed": state["speed"] + (jitter if is_at_target else 0),
            "load": 65.0 + (jitter / 2) if is_at_target else 25.0,
            "message": "🟢 MOTOR ACCELERATING..." if not is_at_target else "🟢 RUNNING - NOMINAL",
            "color": "#22c55e"
        })
    elif start_signal and requires_sensor and not sensor_signal:
        state.update({"message": "🟡 WAITING: Awaiting Sensor Input", "color": "#eab308"})
    else:
        state.update({"message": "🔵 IDLE: Ready to Start", "color": "#3b82f6"})

    return state, state["speed"]

def convert_to_pdf(text):
    """Safely converts Markdown to PDF. Sanitizes headers to prevent id-mapping errors."""
    sanitized_text = re.sub(r'\{#.*?\}', '', text)
    
    buf = BytesIO()
    try:
        pdf = MarkdownPdf(toc_level=0)
        pdf.add_section(Section(sanitized_text))
        pdf.save_bytes(buf)
    except Exception:
        try:
            fallback_text = sanitized_text.replace("# ", "**").replace("#", "")
            pdf_fb = MarkdownPdf(toc_level=0)
            pdf_fb.add_section(Section(fallback_text))
            pdf_fb.save_bytes(buf)
        except Exception as e:
            st.error(f"Critical PDF Error: {e}")
            return b""
            
    return buf.getvalue()

def convert_to_word(text):
    """Converts Markdown text to a .docx file using temporary storage."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tw, \
          tempfile.NamedTemporaryFile(delete=False, suffix=".md", mode='w', encoding='utf-8') as tm:
        tm.write(text)
        tm_path = tm.name
        tw_path = tw.name
    
    try:
        markdown_to_word(tm_path, tw_path)
        with open(tw_path, "rb") as f:
            data = f.read()
    finally:
        if os.path.exists(tm_path): os.remove(tm_path)
        if os.path.exists(tw_path): os.remove(tw_path)
        
    return data