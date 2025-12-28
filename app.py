import streamlit as st
import brain
import validator
import time
import requests
from streamlit_lottie import st_lottie

# --- PROFESSIONAL CONFIGURATION ---
st.set_page_config(page_title="NeuralLogic Pro AI", page_icon="⚡", layout="wide")

# SAFE LOTTIE LOADING FUNCTION
@st.cache_data(ttl=3600)
def load_lottieurl(url: str):
    try:
        r = requests.get(url, timeout=5)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

# Load Assets
lottie_motor = load_lottieurl("https://lottie.host/75f3e971-87a3-4a7b-84e9-11494548489c/nN6Y6YpS5m.json")
lottie_sidebar = load_lottieurl("https://lottie.host/809c3132-7208-412f-98c4-c812d8a43f87/D1U190k6jS.json")

# --- INDUSTRIAL MIDNIGHT UI STYLING ---
st.markdown("""
    <style>
    .main { background-color: #f8fafc; color: #1e293b; font-family: 'Segoe UI', sans-serif; }
    [data-testid="stSidebar"] { background-color: #0f172a; color: #f8fafc; border-right: 2px solid #1e293b; }
    .tip-box { background-color: rgba(245, 158, 11, 0.15); border-left: 5px solid #f59e0b; padding: 15px; border-radius: 4px; color: #fbbf24; font-size: 0.9rem; margin-top: 25px; }
    .stButton>button { background-color: #334155; color: white; border-radius: 4px; border: 1px solid #475569; font-weight: 600; width: 100%; }
    .stTabs [data-baseweb="tab-list"] { background-color: #e2e8f0; border-radius: 8px; padding: 5px; gap: 5px; }
    .sim-status { padding: 20px; border-radius: 10px; text-align: center; color: white; font-weight: bold; font-size: 1.2rem; }
    </style>
    """, unsafe_allow_html=True)

with st.sidebar:
    # --- LOGO ANIMATION (LEFT CORNER) ---
    if lottie_sidebar:
        st_lottie(lottie_sidebar, height=120, key="sidebar_logo")
    else:
        st.markdown("# ⚡ NeuralLogic")
    
    st.markdown("## ⚙️ Settings")
    st.divider()
    plc_brand = st.selectbox("Select Target Hardware", ["Siemens TIA Portal", "Beckhoff TwinCAT", "Rockwell Studio 5000", "CODESYS"])
    if st.button("♻️ Reset Project"):
        st.session_state.clear()
        st.rerun()
    st.markdown('<div class="tip-box"><strong>💡 Pro Tip:</strong> Always include <code>E_STOP</code> in your logic description to pass industrial safety validation.</div>', unsafe_allow_html=True)

st.title("⚡ NeuralLogic AI: Industrial PLC IDE")
user_query = st.text_area("Describe machine logic:", height=150, placeholder="Example: When System_Start is pressed and E_STOP is clear, start the Conveyor_Motor...")

if st.button("🚀 Generate Industrial Project"):
    if user_query:
        with st.spinner("⚡ Synthesizing Engineering Logic..."):
            full_raw = brain.generate_plc_code(user_query, plc_brand)
            try:
                st_part = full_raw.split("---LADDER_START---")[0] if "---LADDER_START---" in full_raw else full_raw
                lad_part = full_raw.split("---LADDER_START---")[1].split("---XML_START---")[0] if "---LADDER_START---" in full_raw else ""
                xml_part = full_raw.split("---XML_START---")[1] if "---XML_START---" in full_raw else ""
                
                code = validator.fix_st_code(validator.extract_code_only(st_part))
                manual = brain.generate_documentation(code, plc_brand)
                st.session_state.stored_project = {"code": code, "lad": lad_part, "xml": xml_part, "man": manual}
            except Exception as e:
                st.error(f"Generation Fault: {str(e)}")

if st.session_state.get("stored_project"):
    res = st.session_state.stored_project
    tags = validator.extract_tags(res["code"])
    col_main, col_diag = st.columns([2, 1])

    with col_main:
        tabs = st.tabs(["💻 PLC Project Code", "🧗 Ladder Logic", "📖 Technical Manual", "🕹️ Digital Twin Dashboard"])
        
        with tabs[0]:
            st.code(res["code"], language="iecst")
            st.download_button("💾 Download .st", data=res["code"], file_name="logic.st", use_container_width=True)
        
        with tabs[1]:
            st.code(res["lad"], language="text")
            st.divider()
            hw_xml = brain.generate_xml_extension(res["code"], tags)
            st.download_button("🔌 Download Hardware XML", data=hw_xml, file_name="PLC_Import.xml", mime="application/xml", use_container_width=True)
        
        with tabs[2]:
            st.markdown(res["man"])
            st.divider()
            st.write("### 📤 Export Manual")
            c1, c2, c3 = st.columns(3)
            with c1: st.download_button("📕 PDF", data=brain.convert_to_pdf(res["man"]), file_name="Manual.pdf", use_container_width=True)
            with c2: st.download_button("📘 Word", data=brain.convert_to_word(res["man"]), file_name="Manual.docx", use_container_width=True)
            with c3: st.download_button("📄 Markdown", data=res["man"], file_name="Manual.md", use_container_width=True)

        with tabs[3]:
            st.subheader("🕹️ Digital Twin Dashboard")
            
            # --- INPUT CONTROLS ---
            c_sys1, c_sys2, c_sys3 = st.columns([1, 1, 2])
            master_start = c_sys1.toggle("🟩 MASTER START", key="master_toggle")
            estop = c_sys2.toggle("🚨 E-STOP", value=True, key="estop_toggle")
            
            current_inputs = {}
            col_viz, col_io = st.columns([2, 1])

            with col_io:
                st.write("**📥 Live Field I/O Signals**")
                for tag, dtype in tags:
                    if "E_STOP" not in tag.upper():
                        current_inputs[tag] = st.checkbox(f"Signal: {tag}", key=f"cb_{tag}")

            # CALCULATE LOGIC
            sim_state, _ = brain.simulate_logic(current_inputs, estop, master_start, time.time(), False)

            with c_sys3:
                st.markdown(f"""
                <div class="sim-status" style="background:{sim_state['color']}; border: 2px solid rgba(0,0,0,0.1);">
                    <h3 style="margin:0; color:white; font-family:monospace;">{sim_state['message']}</h3>
                </div>
                """, unsafe_allow_html=True)

            with col_viz:
                st.write("**📊 Real-Time Telemetry**")
                m1, m2, m3 = st.columns(3)
                m1.metric("Motor Speed", f"{sim_state['speed']} RPM")
                m2.metric("Motor Load", f"{sim_state['load']}%")
                m3.metric("System Health", f"{sim_state['health']}%")
                
                # Visual Feedback: Animation vs Interlock
                if estop:
                    st.image("https://cdn-icons-png.flaticon.com/512/564/564619.png", width=150)
                    st.error("Interlock: E-Stop Active")
                elif sim_state['active'] and lottie_motor:
                    st_lottie(lottie_motor, height=250, key="motor_anim")
                else:
                    st.image("https://cdn-icons-png.flaticon.com/512/3043/3043813.png", width=150)
                    st.caption("System Standby - Awaiting Signals")

    with col_diag:
        st.subheader("🛡️ Safety & Status")
        if any(x in res["code"].upper() for x in ["E_STOP", "ESTOP"]):
            st.success("✅ E-STOP Safety Logic Detected")
        else:
            st.error("🚨 Safety Warning: No 'E_STOP' detected.")
        
        st.subheader("📋 I/O Tag Mapping")
        st.table([{"Tag Name": t[0], "Data Type": t[1]} for t in tags])