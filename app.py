import streamlit as st
import brain
import validator
import time
import requests
import re
from streamlit_lottie import st_lottie

# --- PROFESSIONAL CONFIGURATION ---
st.set_page_config(page_title="PLCify Pro AI", page_icon="⚡", layout="wide")

# SAFE LOTTIE LOADING FUNCTION
@st.cache_data(ttl=3600)
def load_lottieurl(url: str):
    try:
        r = requests.get(url, timeout=5)
        if r.status_code != 200: return None
        return r.json()
    except: return None

# Load Assets
lottie_motor = load_lottieurl("https://lottie.host/75f3e971-87a3-4a7b-84e9-11494548489c/nN6Y6YpS5m.json")
lottie_sidebar = load_lottieurl("https://lottie.host/809c3132-7208-412f-98c4-c812d8a43f87/D1U190k6jS.json")

# --- INDUSTRIAL MIDNIGHT UI STYLING ---
st.markdown("""
    <style>
    .main { background-color: #f8fafc; color: #1e293b; font-family: 'Segoe UI', sans-serif; }
    
    /* RAILS AND RUNGS VISUALIZER CONTAINER */
    .ladder-container {
        font-family: 'Courier New', Courier, monospace !important;
        background-color: #0f172a;
        color: #38bdf8;
        padding: 25px;
        border-radius: 8px;
        line-height: 1.1;
        white-space: pre !important;
        overflow-x: auto;
        border: 2px solid #1e293b;
        font-size: 14px;
        margin-bottom: 20px;
    }

    /* SIDEBAR STYLING */
    [data-testid="stSidebar"] { 
        background-color: #0f172a !important; 
        color: #f8fafc !important; 
        border-right: 2px solid #1e293b; 
    }
    
    [data-testid="stSidebar"] .stMarkdown, 
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] p { 
        color: #f8fafc !important; 
        opacity: 1 !important;
    }

    /* History Button Styles */
    [data-testid="stSidebar"] .stButton > button {
        background-color: #1e293b !important;
        color: #f8fafc !important;
        border: 1px solid #334155 !important;
        text-align: left;
    }
    
    /* Discrete Delete Cross */
    div[data-testid="column"] button[key^="del_"] {
        background-color: transparent !important;
        border: none !important;
        color: #94a3b8 !important;
        padding: 0px !important;
    }
    div[data-testid="column"] button[key^="del_"]:hover { color: #ef4444 !important; }

    .scada-status-bar {
        padding: 12px; border-radius: 6px; text-align: center; color: white;
        font-weight: 800; font-family: 'Courier New', monospace; letter-spacing: 2px;
        text-transform: uppercase; box-shadow: inset 0 0 10px rgba(0,0,0,0.2); margin-bottom: 20px;
    }
    
    .tip-box { background-color: rgba(245, 158, 11, 0.15); border-left: 5px solid #f59e0b; padding: 15px; border-radius: 4px; color: #fbbf24; font-size: 0.9rem; margin-top: 25px; }
    .stTabs [data-baseweb="tab-list"] { background-color: #e2e8f0; border-radius: 8px; padding: 5px; gap: 5px; }
    </style>
    """, unsafe_allow_html=True)

# Initialize Session States
if "sim_speed" not in st.session_state: st.session_state.sim_speed = 0
if "history" not in st.session_state: st.session_state.history = []
if "input_text" not in st.session_state: st.session_state.input_text = ""
if "stored_project" not in st.session_state: st.session_state.stored_project = None

# --- SIDEBAR: History & Settings ---
with st.sidebar:
    if lottie_sidebar:
        st_lottie(lottie_sidebar, height=100, key="sidebar_logo")
    
    st.markdown("### 📜 Project History")
    for i, hist_item in enumerate(st.session_state.history):
        h_col1, h_col2 = st.columns([5, 1])
        with h_col1:
            if st.button(f"💬 {hist_item[:18]}...", key=f"h_{i}", use_container_width=True):
                st.session_state.input_text = hist_item
                st.rerun()
        with h_col2:
            if st.button("✕", key=f"del_{i}"):
                st.session_state.history.pop(i)
                st.rerun()

    st.divider()
    st.markdown("### ⚙️ Hardware Settings")
    plc_brand = st.selectbox("Select Target Hardware", ["Siemens TIA Portal", "Beckhoff TwinCAT", "Rockwell Studio 5000", "CODESYS"])
    
    if st.button("♻️ Reset Project", use_container_width=True):
        st.session_state.clear()
        st.rerun()
    st.markdown('<div class="tip-box"><strong>💡 Pro Tip:</strong> Always include <code>E_STOP</code> for safety validation.</div>', unsafe_allow_html=True)

# --- MAIN INTERFACE ---
st.title("⚡ PLCIFY: Industrial PLC IDE")
user_query = st.text_area("Describe machine logic:", value=st.session_state.input_text, height=150, placeholder="Example: Start motor when Sensor is high...")

if st.button("🚀 Generate Industrial Project", use_container_width=True):
    if not user_query.strip():
        st.error("⚠️ Logic Description Required.")
    else:
        st.session_state.stored_project = None
        if user_query not in st.session_state.history:
            st.session_state.history.insert(0, user_query)
            st.session_state.history = st.session_state.history[:5]
        
        with st.spinner("⚡ Synthesizing Engineering Logic..."):
            try:
                full_raw = brain.generate_plc_code(user_query, plc_brand)
                st_part = full_raw.split("---LADDER_START---")[0] if "---LADDER_START---" in full_raw else full_raw
                lad_part = full_raw.split("---LADDER_START---")[1].split("---XML_START---")[0] if "---LADDER_START---" in full_raw else ""
                
                code = validator.fix_st_code(validator.extract_code_only(st_part))
                manual = brain.generate_documentation(code, plc_brand)
                
                st.session_state.stored_project = {"code": code, "lad": lad_part, "man": manual}
                st.rerun()
            except Exception as e:
                st.error(f"Generation Fault: {str(e)}")

# --- RESULTS DISPLAY ---
if st.session_state.get("stored_project"):
    res = st.session_state.stored_project
    tags = validator.extract_tags(res["code"])
    col_main, col_diag = st.columns([2, 1])

    with col_main:
        tabs = st.tabs(["💻 PLC Project Code", "🧗 Ladder Logic", "📖 Technical Manual", "🕹️ Digital Twin Dashboard"])
        
        with tabs[0]:
            st.code(res["code"], language="iecst")
            st.download_button("💾 Download .st", data=res["code"], file_name="logic.st", key="dl_st", use_container_width=True)
        
        with tabs[1]:
            st.write(f"### 🧗 {plc_brand} Visual Rails and Rungs")
            # Forcing monospace alignment for the Rail and Rung style
            st.markdown(f'<div class="ladder-container">{res["lad"]}</div>', unsafe_allow_html=True)
            st.divider()
            
            hw_data, extension, mime_type = brain.generate_hardware_export(res["code"], tags, plc_brand)
            st.download_button(
                label=f"🔌 Download Hardware Project ({extension})",
                data=hw_data,
                file_name=f"NeuralLogic_Export{extension}",
                mime=mime_type,
                use_container_width=True,
                help=f"Download native {plc_brand} import file."
            )
        
        with tabs[2]:
            st.markdown(res["man"])
            st.divider()
            c1, c2, c3 = st.columns(3)
            with c1: st.download_button("📕 PDF", data=brain.convert_to_pdf(res["man"]), file_name="Manual.pdf", use_container_width=True)
            with c2: st.download_button("📘 Word", data=brain.convert_to_word(res["man"]), file_name="Manual.docx", use_container_width=True)
            with c3: st.download_button("📄 Markdown", data=res["man"], file_name="Manual.md", use_container_width=True)

        with tabs[3]:
            st.subheader("🕹️ Digital Twin Dashboard")
            c_sys1, c_sys2 = st.columns([1, 1])
            master_start = c_sys1.toggle("🟩 MASTER START", key="master_toggle")
            estop = c_sys2.toggle("🚨 E-STOP", value=True, key="estop_toggle")
            
            st.divider()
            current_inputs = {}
            col_viz, col_io = st.columns([2, 1])

            with col_io:
                st.write("**📥 Live Field I/O Signals**")
                for tag, dtype in tags:
                    if "E_STOP" not in tag.upper():
                        current_inputs[tag] = st.checkbox(f"Signal: {tag}", key=f"cb_{tag}")

            sim_state, new_speed = brain.simulate_logic(current_inputs, estop, master_start, st.session_state.sim_speed)
            st.session_state.sim_speed = new_speed

            with col_viz:
                st.markdown(f'<div class="scada-status-bar" style="background:{sim_state["color"]};">{sim_state["message"]}</div>', unsafe_allow_html=True)
                m1, m2, m3 = st.columns(3)
                m1.metric("Motor Speed", f"{int(sim_state['speed'])} RPM")
                m2.metric("Motor Load", f"{sim_state['load']}%")
                m3.metric("System Health", f"{sim_state['health']}%")
                
                if estop:
                    st.image("https://cdn-icons-png.flaticon.com/512/564/564619.png", width=120)
                elif sim_state['active'] and lottie_motor:
                    st_lottie(lottie_motor, height=250, key="motor_anim")
                else:
                    st.image("https://cdn-icons-png.flaticon.com/512/3043/3043813.png", width=120)

    with col_diag:
        st.subheader("🛡️ Safety & Status")
        if any(x in res["code"].upper() for x in ["E_STOP", "ESTOP"]):
            st.success("✅ E-STOP Safety Logic Detected")
        else:
            st.error("🚨 Safety Warning: No 'E_STOP' detected.")
        st.table([{"Tag Name": t[0], "Data Type": t[1]} for t in tags])