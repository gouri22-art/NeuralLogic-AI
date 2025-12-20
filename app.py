import streamlit as st
import brain  # This imports the brain.py file we made earlier
import validator # This will be our safety filter

# Streamlit automatically looks in secrets.toml (local) or Cloud Secrets (online)
api_key = st.secrets["GROQ_API_KEY"]

st.set_page_config(page_title="NeuralLogic AI", page_icon="🤖")

st.title("🤖 NeuralLogic AI")
st.subheader("Convert Natural Language to Industrial PLC Code")

# Sidebar for instructions
with st.sidebar:
    st.info("Example: 'Start motor A when sensor B is high, wait 5 seconds, then stop.'")
    st.warning("All code includes a mandatory Safety E-Stop.")

# User Input
user_query = st.text_area("Describe your machine logic:", placeholder="Type instructions here...")

if st.button("Generate PLC Code"):
    if user_query:
        with st.spinner("Engineering..."):
            raw_output = brain.generate_plc_code(user_query)
            
            # 1. Extract and Fix
            clean_code = validator.extract_code_only(raw_output)
            fixed_code = validator.fix_st_code(clean_code)
            
            # 2. Validate
            errors = validator.validate_st_code(fixed_code)
            
            # 3. UI logic
            if not errors:
                st.success("✅ Code Generated!")
            else:
                with st.expander("⚠️ View Syntax Warnings"):
                    for err in errors:
                        st.write(err)

            # --- DISPLAY THE CODE ---
            st.code(fixed_code, language='iecst')

            # --- PLACE DOWNLOAD BUTTON HERE ---
            # It must be inside this 'if' block so 'fixed_code' is defined!
            st.download_button(
                label="Download .ST File",
                data=fixed_code,
                file_name="plc_logic.st",
                mime="text/plain"
            )
    else:
        st.error("Please enter a description first.")