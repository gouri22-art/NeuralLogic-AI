import os
import streamlit as st
from groq import Groq
from markdown_pdf import MarkdownPdf, Section
from io import BytesIO
import tempfile
from md2docx_python.src.md2docx_python import markdown_to_word
import time

def get_client():
    api_key = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")
    if not api_key:
        st.error("GROQ_API_KEY not found.")
    return Groq(api_key=api_key)

def generate_plc_code(user_instruction, brand):
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
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_instruction}
        ],
        temperature=0.1
    )
    return completion.choices[0].message.content

def generate_documentation(code, brand):
    client = get_client()
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "user", "content": f"Create a professional Technical Manual for this {brand} code:\n{code}"}
        ]
    )
    return completion.choices[0].message.content

def generate_xml_extension(st_code, tags):
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

def simulate_logic(inputs, estop, master_start, last_run_time, has_timer):
    state = {
        "active": False,
        "speed": 0,
        "load": 0.0,
        "health": 100,
        "message": "System Ready",
        "color": "#94a3b8" 
    }

    # 1. HARD-WIRED INTERLOCKS
    if estop:
        state.update({"message": "🚨 EMERGENCY STOP ACTIVE", "color": "#ef4444", "health": 0})
        return state, 0
    
    if not master_start:
        state.update({"message": "⚪ STANDBY: Master Start Off", "color": "#64748b"})
        return state, 0

    # 2. DYNAMIC TAG DETECTION
    start_signal = any(v for k, v in inputs.items() if any(x in k.upper() for x in ["START", "RUN", "MOTOR"]))
    sensor_signal = any(v for k, v in inputs.items() if any(x in k.upper() for x in ["SENSOR", "PROX", "SWITCH"]))
    fault_signal = any(v for k, v in inputs.items() if any(x in k.upper() for x in ["FAULT", "OVERLOAD", "ERR"]))

    if fault_signal:
        state.update({"message": "🔴 SYSTEM FAULT DETECTED", "color": "#b91c1c", "health": 20})
        return state, 0

    # 3. OPERATION LOGIC
    requires_sensor = any("SENSOR" in k.upper() for k in inputs.keys())
    
    if start_signal:
        if requires_sensor and not sensor_signal:
            state.update({"message": "🟡 WAITING: Awaiting Sensor", "color": "#eab308", "active": False})
        else:
            # SYSTEM RUNNING
            jitter = (int(time.time() * 10) % 12)
            state.update({
                "active": True,
                "speed": 1750 + jitter,
                "load": 68.5 + (jitter/2),
                "message": "🟢 CONVEYOR RUNNING - NOMINAL",
                "color": "#22c55e"
            })
    else:
        state.update({"message": "🔵 IDLE: Awaiting Start Signal", "color": "#3b82f6"})

    return state, 0

def convert_to_pdf(text):
    pdf = MarkdownPdf(toc_level=0)
    pdf.add_section(Section(text))
    buf = BytesIO()
    pdf.save_bytes(buf)
    return buf.getvalue()

def convert_to_word(text):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tw, \
         tempfile.NamedTemporaryFile(delete=False, suffix=".md", mode='w', encoding='utf-8') as tm:
        tm.write(text)
        tm_path = tm.name
    markdown_to_word(tm_path, tw.name)
    with open(tw.name, "rb") as f:
        data = f.read()
    return data