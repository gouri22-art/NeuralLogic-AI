import re

def extract_code_only(text):
    """Removes markdown code blocks and section headers from AI response."""
    # Clean up section markers
    text = text.replace("---LADDER_START---", "").replace("---XML_START---", "")
    
    # Regex to find code within triple backticks
    code_pattern = r"```(?:iecst|pascal|text|xml)?\s*(.*?)\s*```"
    matches = re.findall(code_pattern, text, re.DOTALL)
    
    if matches:
        return matches[0].strip()
    return text.strip()

def fix_st_code(code):
    """Ensures Industrial Safety Compliance via Auto-Injection."""
    fixed_code = code.strip()
    upper_code = fixed_code.upper()
    
    # SAFETY INJECTION: If no E_STOP logic exists, wrap the entire code
    if "E_STOP" not in upper_code and "ESTOP" not in upper_code:
        safety_header = "VAR\n    E_STOP : BOOL; (* Auto-Injected Safety *)\nEND_VAR\n\n"
        fixed_code = f"{safety_header}IF NOT E_STOP THEN\n    {fixed_code}\nEND_IF;"
    
    # Check for unclosed IF statements (common AI error)
    if_count = upper_code.count("IF ")
    endif_count = upper_code.count("END_IF")
    
    if if_count > endif_count:
        missing = if_count - endif_count
        fixed_code += "\n" + "\n".join(["END_IF;"] * missing)
        
    return fixed_code

def extract_tags(code):
    """Parses Structured Text to identify I/O Tags and Data Types."""
    # Pattern to find variable declarations like 'Sensor_1 : BOOL;'
    pattern = r'(\w+)\s*(?:AT\s+[\%\w\.]+\s*)?:\s*(\w+)\s*;'
    matches = re.findall(pattern, code, re.IGNORECASE)
    
    unique_tags = {}
    for name, dtype in matches:
        name_up = name.upper()
        # Filter out keywords that might look like variables
        if name_up not in ['VAR', 'END_VAR', 'PROGRAM', 'END_PROGRAM', 'IF', 'THEN', 'ELSE']:
            unique_tags[name_up] = (name, dtype)
            
    # Always ensure E_STOP is in the tag list if it's in the code
    if "E_STOP" in code.upper() and "E_STOP" not in unique_tags:
        unique_tags["E_STOP"] = ("E_STOP", "BOOL")
        
    return list(unique_tags.values())