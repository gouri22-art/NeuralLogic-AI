import streamlit as st
import brain
import validator

st.set_page_config(page_title="NeuralLogic Pro", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    .stTabs [data-baseweb="tab"] { background-color: #f0f2f6; border-radius: 4px; padding: 8px 16px; font-weight: bold; }
    .stTabs [aria-selected="true"] { border-top: 4px solid #ff4b4b; background-color: #ffffff; }
    </style>
    """, unsafe_allow_html=True)

st.title("⚡ NeuralLogic AI: Industrial PLC IDE")

with st.sidebar:
    st.header("Settings")
    plc_brand = st.selectbox("Select Target PLC Hardware", 
                             ["Siemens TIA Portal", "Beckhoff TwinCAT", "Rockwell Studio 5000", "CODESYS Standard"])
    st.divider()
    st.info("💡 Tip: Always include 'E_STOP' in your description for safety validation.")
    st.caption("Version: 5.4 (Strict Syntax Mode)")

user_query = st.text_area("Describe your machine logic:", 
                          placeholder="e.g., Start Motor_Start when Sensor_B is TRUE...",
                          height=150)

if st.button("🚀 Generate Industrial Project"):
    if user_query:
        with st.spinner(f"Engineering full project for {plc_brand}..."):
            raw_output = brain.generate_plc_code(user_query, plc_brand)
            clean_code = validator.extract_code_only(raw_output)
            fixed_code = validator.fix_st_code(clean_code)
            manual_text = brain.generate_documentation(fixed_code, plc_brand)
            tags = validator.extract_tags(fixed_code)
            errors = validator.validate_st_code(fixed_code)

            col1, col2 = st.columns([2, 1])
            with col1:
                tab_code, tab_manual = st.tabs(["💻 PLC Project Code", "📖 Technical Manual & Downloads"])
                
                with tab_code:
                    st.code(fixed_code, language='iecst')
                    st.download_button("💾 Download PLC Code (.ST)", fixed_code, "plc_logic.st")

                with tab_manual:
                    st.markdown(manual_text)
                    st.divider()
                    st.subheader("📂 Professional Exports")
                    
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        st.download_button("📥 Markdown", manual_text, "manual.md")
                    with c2:
                        st.download_button("📕 PDF Document", brain.convert_to_pdf(manual_text), "manual.pdf", "application/pdf")
                    with c3:
                        st.download_button("📘 Word Document", brain.convert_to_word(manual_text), "manual.docx")

            with col2:
                st.subheader("🛡️ Safety & Status")
                if not errors:
                    st.success("✅ Brand Safety Validated")
                else:
                    for err in errors:
                        st.warning(err)
                
                if tags:
                    st.subheader("📋 I/O Tag Mapping")
                    st.table({"Variable": [t[0] for t in tags], "Data Type": [t[1] for t in tags]})
    else:
        st.error("Please enter machine instructions first.")