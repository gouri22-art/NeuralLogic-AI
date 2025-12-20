import re

def extract_code_only(text):
    pattern = r"(VAR|PROGRAM)[\s\S]+?(END_IF;|END_VAR;|END_VAR|;)(?!\s*[\w])"
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(0) if match else text

def extract_tags(code):
    """Finds variables like 'Motor_Start : BOOL;' and returns a list of tuples."""
    return re.findall(r"(\w+)\s*:\s*(\w+);", code)

def validate_st_code(code):
    errors = []
    if "E_STOP" not in code.upper():
        errors.append("🚨 Safety Warning: No 'E_STOP' detected.")
    if code.upper().count("IF ") > code.upper().count("END_IF"):
        errors.append("❌ Syntax Error: Unclosed IF statement.")
    return errors

def fix_st_code(code):
    fixed_code = code.strip()
    if_count = fixed_code.upper().count("IF ")
    end_if_count = fixed_code.upper().count("END_IF")
    if if_count > end_if_count:
        fixed_code += "\n" + "\n".join(["END_IF;"] * (if_count - end_if_count))
    return fixed_code