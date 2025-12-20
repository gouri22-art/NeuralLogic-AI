import streamlit as st
import brain
import validator

st.set_page_config(page_title="NeuralLogic Pro", page_icon="⚡", layout="wide")

st.title("⚡ NeuralLogic AI: Industrial PLC IDE")

# --- SIDEBAR CONFIGURATION ---
with st.sidebar:
    st.header("Settings")
    plc_brand = st.selectbox("Select Target PLC Hardware", 
                             ["Siemens TIA Portal", "Beckhoff TwinCAT", "Rockwell Studio 5000", "CODESYS Standard"])
    st.divider()
    st.info("💡 Tip: Always include 'E_STOP' in your description for safety validation.")

# --- MAIN INTERFACE ---
user_query = st.text_area("Describe your machine logic:", 
                          placeholder="e.g., Start motor A when sensor B is high, stop after 10 seconds...",
                          height=150)

col1, col2 = st.columns([2, 1])

if st.button("🚀 Generate & Validate Logic"):
    if user_query:
        with st.spinner(f"Engineering {plc_brand} code..."):
            # 1. Processing
            raw_output = brain.generate_plc_code(user_query, plc_brand)
            clean_code = validator.extract_code_only(raw_output)
            fixed_code = validator.fix_st_code(clean_code)
            
            # 2. Validation
            errors = validator.validate_st_code(fixed_code)
            tags = validator.extract_tags(fixed_code)

            with col1:
                st.subheader(f"Generated Code ({plc_brand})")
                st.code(fixed_code, language='iecst')
                
                st.download_button(
                    label="💾 Download .ST File",
                    data=fixed_code,
                    file_name="logic.st",
                    mime="text/plain"
                )

            with col2:
                st.subheader("Safety & Status")
                if not errors:
                    st.success("✅ Code is Safety Compliant")
                else:
                    for err in errors:
                        st.warning(err)
                
                if tags:
                    st.subheader("📋 IO Tag List")
                    st.table({"Variable": [t[0] for t in tags], "Type": [t[1] for t in tags]})
    else:
        st.error("Please enter instructions first.")