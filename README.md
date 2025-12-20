# ⚡ NeuralLogic AI: Industrial PLC IDE
> **AI-Powered Structured Text Generation & Safety Validation for Industrial Automation.**

NeuralLogic AI is a professional-grade tool that converts natural language instructions into industrial-standard PLC code (IEC 61131-3). It handles the complex syntax of Structured Text while ensuring safety protocols like E-STOPs are integrated from the start.

![GenAI Badge](https://img.shields.io/badge/GenAI-Automation-orange?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)

## 🚀 Key Features
- **Multi-Brand Support:** Specialized code generation for **Siemens TIA Portal**, **Beckhoff TwinCAT**, **Rockwell Studio 5000**, and **CODESYS**.
- **Safety Auditor:** Scans code for missing emergency stop logic (`E_STOP`) and warns the user.
- **Auto-Fixer:** Automatically repairs common AI errors like missing `END_IF` tags or unclosed variable blocks.
- **Live IO Tag List:** Automatically extracts variables to create a hardware assignment table.
- **Industrial Export:** Download your logic as a `.st` file ready for import into professional PLC environments.

---

## 🛠️ Installation & Setup

Follow these steps to get the project running on your local machine.

### 1. Prerequisites
- **Python 3.8+** installed.
- A **Groq API Key** (Get one for free at [console.groq.com](https://console.groq.com/)).

### 2. Clone the Repository
```bash
git clone [https://github.com/YOUR_USERNAME/NeuralLogic-AI.git](https://github.com/YOUR_USERNAME/NeuralLogic-AI.git)
cd NeuralLogic-AI

# 🛠️ Installation & Local Setup

### 3. Install Dependencies
Install the required Python libraries using the command below:
```bash
pip install streamlit groq python-dotenv

### 4. Configure Your API Key
For the app to work, you must add your Groq API key to a secrets file.

1 Create a folder named .streamlit in the project root.

2 Create a file named secrets.toml inside that folder.

3 Paste the following line into secrets.toml:
    
    GROQ_API_KEY = "your_actual_groq_api_key_here"

5. Launch the App
Bash

streamlit run app.py
📖 How to Use
Select Hardware: Use the sidebar to choose your target PLC brand (e.g., Siemens TIA Portal).

Describe Logic: Type your requirement in the text area (e.g., "Start the fan if temperature > 50°C").

Generate: Click 🚀 Generate & Validate Logic.

Review & Download: Inspect the generated code and the tag table, then hit Download to save the .st file.

📂 Project Organization
app.py: The main user interface and dashboard.

brain.py: The logic engine that communicates with the Llama 3.3 model.

validator.py: The "Safety Layer" that cleans, extracts, and repairs the generated code.

🔒 Safety Disclaimer
Prototyping Only: This tool is an AI assistant. All generated code must be reviewed and tested in a safe, simulated environment by a certified professional before being deployed to live industrial hardware.

Developed with ❤️ by Prajakta Kudale