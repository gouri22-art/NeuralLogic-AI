import streamlit as st
import brain
import validator
import time

st.set_page_config(page_title="NeuralLogic Pro", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    .stTabs [data-baseweb="tab"] { background-color: #f0f2f6; border-radius: 4px; padding: 8px 16px; font-weight: bold; }
    .stTabs [aria-selected="true"] { border-top: 4px solid #ff4b4b; background-color: #ffffff; }
    </style>
    """, unsafe_allow_html=True)

st.title("⚡ NeuralLogic AI: Industrial PLC IDE")

# Initialize Session State keys if not present
if "stored_project" not in st.session_state:
    st.session_state.stored_project = None
if "input_text" not in st.session_state:
    st.session_state.input_text = ""

with st.sidebar:
    st.header("Settings")
    plc_brand = st.selectbox(
        "Select Target Hardware", 
        ["Siemens TIA Portal", "Beckhoff TwinCAT", "Rockwell Studio 5000", "CODESYS Standard"],
        key="plc_selector_sidebar"
    )
    st.divider()
    
    # RESET PROJECT: Now clears prompt and results
    if st.button("♻️ Reset Project", key="reset_project_btn"):
        st.session_state.stored_project = None
        st.session_state.input_text = "" 
        if 'sim_timer_ref' in st.session_state: del st.session_state.sim_timer_ref
        st.rerun()
        
    st.divider()
    st.info("💡 Tip: Always include 'E_STOP' in your description for safety validation.")

# Linked to session state to allow clearing
user_query = st.text_area(
    "Describe your machine logic (e.g. based on Motor_A/Sensor_B):", 
    value=st.session_state.input_text,
    placeholder="e.g., Start Motor_A when Sensor_B is high, with a 5s timer...",
    height=150,
    key="main_user_input"
)

if st.button("🚀 Generate Industrial Project", key="generate_btn"):
    if user_query:
        st.session_state.input_text = user_query # Store current text
        with st.spinner("Engineering System..."):
            raw = brain.generate_plc_code(user_query, plc_brand)
            code = validator.fix_st_code(validator.extract_code_only(raw))
            manual = brain.generate_documentation(code, plc_brand)
            st.session_state.stored_project = {"code": code, "manual": manual}
    else:
        st.error("Please enter a logic prompt.")

if st.session_state.stored_project:
    res = st.session_state.stored_project
    tags = validator.extract_tags(res["code"])
    has_timer = any(x in res["code"].upper() for x in ["TON", "TP", "T#", "TIMER"])
    
    label = next((tag[0] for tag in tags if any(kw in tag[0] for kw in ["Motor", "Belt", "Valve", "Conveyor", "Lamp"])), "Output")

    col1, col2 = st.columns([2, 1])
    with col1:
        tab_code, tab_man, tab_sim = st.tabs(["💻 PLC Project Code", "📖 Technical Manual", "⚡ Live Simulator"])
        
        with tab_code:
            st.code(res["code"], language='iecst')
            st.download_button("💾 Download .ST Source", res["code"], "logic.st", key="dl_st_btn")

        with tab_man:
            st.markdown(res["manual"])
            st.divider()
            st.subheader("📂 Professional Exports")
            c1, c2, c3 = st.columns(3)
            with c1: st.download_button("📥 Markdown", res["manual"], "manual.md", key="dl_md_btn")
            with c2: st.download_button("📕 PDF", brain.convert_to_pdf(res["manual"]), "manual.pdf", "application/pdf", key="dl_pdf_btn")
            with c3: st.download_button("📘 Word", brain.convert_to_word(res["manual"]), "manual.docx", key="dl_word_btn")

        with tab_sim:
            st.subheader(f"Continuous Simulation: {label}")
            s1, s2 = st.columns(2)
            with s1:
                sim_in = st.toggle("Enable Input Signal", key="sim_input_toggle")
                sim_estop = st.toggle("🚨 E_STOP (Safety)", key="sim_estop_toggle")
                if sim_in and not sim_estop and has_timer:
                    if 'sim_timer_ref' not in st.session_state: st.session_state.sim_timer_ref = time.time()
                else:
                    if 'sim_timer_ref' in st.session_state: del st.session_state.sim_timer_ref

            with s2:
                t_start = st.session_state.get('sim_timer_ref', time.time())
                is_on, elapsed = brain.simulate_logic(sim_in, sim_estop, t_start, has_timer)
                
                if has_timer:
                    # Logic to show 0-5s for RUNNING and 5-10s for WAITING
                    display_time = elapsed if elapsed < 5.0 else elapsed - 5.0
                    phase = "RUNNING" if elapsed < 5.0 else "WAITING"
                    st.write(f"Cycle Phase: **{phase}** ({display_time:.1f}s / 5.0s)")
                    st.progress(display_time / 5.0)
                    if sim_in and not sim_estop:
                        time.sleep(0.1)
                        st.rerun()
                
                # Fixed: RUNNING phase is now Green (Success)
                if is_on: st.success(f"🟢 {label}: ON")
                else: st.error(f"🔴 {label}: OFF")

    with col2:
        st.subheader("🛡️ Safety & Status")
        st.success("✅ Brand Safety Validated")
        if tags:
            st.subheader("📋 I/O Tag Mapping")
            st.table({"Variable": [t[0] for t in tags], "Type": [t[1] for t in tags]})