import re

def extract_code_only(text):
    """
    Extracts only the PLC code blocks, removing AI chatter.
    It looks for the start of a VAR block and ends at the last END_IF or semicolon.
    """
    # Look for the pattern starting from 'VAR' or 'PROGRAM' 
    # and capturing everything until the last 'END_IF', 'END_VAR', or ';'
    pattern = r"(VAR|PROGRAM)[\s\S]+?(END_IF;|END_VAR;|END_VAR|;)(?!\s*[\w])"
    match = re.search(pattern, text, re.IGNORECASE)
    
    if match:
        return match.group(0)
    
    # Fallback: If no VAR block found, just strip common AI prefixes
    return re.sub(r"^(Here is|Sure|This is).*?\n", "", text, flags=re.IGNORECASE).strip()

def validate_st_code(code):
    # First, clean the code so we don't validate the AI's 'chat'
    clean_code = extract_code_only(code)
    errors = []
    lines = clean_code.split('\n')
    
    # Improved Semicolon Check
    keywords_no_semicolon = ('VAR', 'END_VAR', 'IF', 'THEN', 'ELSE', 'ELSIF', 'PROGRAM', 'END_PROGRAM')
    
    for i, line in enumerate(lines):
        clean_line = line.strip()
        if not clean_line or clean_line.startswith('(*'): continue
            
        if not clean_line.startswith(keywords_no_semicolon):
            if not clean_line.endswith(';') and not clean_line.startswith('END_'):
                if ':=' in clean_line or '(' in clean_line:
                    errors.append(f"⚠️ Missing semicolon on line {i+1}: '{clean_line}'")

    if "E_STOP" not in clean_code.upper():
        errors.append("🚨 Safety Warning: No 'E_STOP' logic detected.")

    if clean_code.upper().count("IF ") > clean_code.upper().count("END_IF"):
        errors.append("❌ Syntax Error: Unclosed IF statement.")
        
    return errors

def fix_st_code(code):
    # Ensure we only fix the actual code part
    code_to_fix = extract_code_only(code)
    
    if_count = code_to_fix.upper().count("IF ")
    end_if_count = code_to_fix.upper().count("END_IF")
    
    if if_count > end_if_count:
        for _ in range(if_count - end_if_count):
            code_to_fix += "\nEND_IF;"
            
    return code_to_fix