def validate_st_code(code_string):
    """Checks if the PLC code follows basic safety rules."""
    code_upper = code_string.upper()
    
    # Rule 1: Must contain an Emergency Stop variable
    if "E_STOP" not in code_upper and "EMERGENCY" not in code_upper:
        return False, "Missing mandatory Emergency Stop (E_STOP) logic."
    
    # Rule 2: Basic Syntax Check (Structured Text blocks)
    if "IF" in code_upper and "END_IF" not in code_upper:
        return False, "Incomplete IF-THEN logic detected."
        
    return True, "Code passed all safety checks."