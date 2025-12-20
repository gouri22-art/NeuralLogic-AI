import streamlit as st
import brain  # This imports the brain.py file we made earlier
import validator # This will be our safety filter

# Streamlit automatically looks in secrets.toml (local) or Cloud Secrets (online)
api_key = st.secrets["OPENAI_API_KEY"]

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
        with st.spinner("AI is engineering your logic..."):
            # 1. Get code from Brain
            raw_code = brain.generate_plc_code(user_query)
            
            # 2. Run through Validator
            is_safe, message = validator.validate_st_code(raw_code)
            
            if is_safe:
                st.success("✅ Code Generated & Safety Verified!")
                st.code(raw_code, language='pascal') # 'pascal' highlights ST code well
            else:
                st.error(f"❌ Safety Violation: {message}")
                st.code(raw_code, language='pascal')
    else:
        st.error("Please enter a description first.")