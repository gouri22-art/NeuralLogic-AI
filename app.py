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

if st.button("🚀 Generate & Validate Logic"):
    if user_query:
        with st.spinner(f"Engineering {plc_brand} code & manual..."):
            # 1. Processing Logic
            raw_output = brain.generate_plc_code(user_query, plc_brand)
            clean_code = validator.extract_code_only(raw_output)
            fixed_code = validator.fix_st_code(clean_code)
            
            # 2. Generating Documentation
            manual_text = brain.generate_documentation(fixed_code, plc_brand)
            
            # 3. Validation & Tags
            errors = validator.validate_st_code(fixed_code)
            tags = validator.extract_tags(fixed_code)

            # --- DISPLAY RESULTS ---
            col1, col2 = st.columns([2, 1])

            with col1:
                # Code Section
                st.subheader(f"💻 Generated Code ({plc_brand})")
                st.code(fixed_code, language='iecst')
                st.download_button(
                    label="💾 Download .ST File",
                    data=fixed_code,
                    file_name="logic.st",
                    mime="text/plain"
                )
                
                st.divider()
                st.subheader("📖 Maintenance Manual")
                st.markdown(manual_text)
                # 1. Row of Download Buttons
                btn_col1, btn_col2, btn_col3 = st.columns(3)
                with btn_col1:
                    st.download_button("📥 Markdown (.md)", manual_text, "manual.md")
                with btn_col2:
                     # Generate PDF on click
                    pdf_data = brain.convert_to_pdf(manual_text)
                    st.download_button("📕 Download PDF", pdf_data, "manual.pdf", "application/pdf")
                with btn_col3:
                     # Generate Word on click
                    word_data = brain.convert_to_word(manual_text)
                    st.download_button("📘 Download Word", word_data, "manual.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")

            with col2:
                # Safety Section
                st.subheader("Safety & Status")
                if not errors:
                    st.success("✅ Code is Safety Compliant")
                else:
                    for err in errors:
                        st.warning(err)
                
                # Tag List Section
                if tags:
                    st.subheader("📋 IO Tag List")
                    st.table({"Variable": [t[0] for t in tags], "Type": [t[1] for t in tags]})
    else:
        st.error("Please enter instructions first.")