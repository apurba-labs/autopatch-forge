import re
from app.core.config import logger

async def analyze_log_payload(error_log: str) -> dict:
    """
    Agent 1: High-speed native log analyzer. Parses complex tracebacks to 
    extract error bounds, file targets, and line numbers instantly.
    """
    logger.info("[AGENT: ANALYZER] Running stream regex trace decoding...")
    
    # Standard Python traceback parsing signature
    # Pattern tracks: File "string.py", line X, in function
    file_line_pattern = r'File\s+[\'"](.+?)[\'"]\s*,\s*line\s+(\d+)'
    error_pattern = r'([\w\d]+Error:\s*.+)'
    
    target_file = "app/utils/helpers.py"  # Default structural fallback
    line_number = 1
    raw_error = "Unknown runtime trace anomaly."
    
    try:
        # Extract file path and line location from the trace stack
        locations = re.findall(file_line_pattern, error_log)
        if locations:
            # Grab the last known execution failure point in the stack
            target_file, line_str = locations[-1]
            line_number = int(line_str)
            
        # Extract the explicit Exception class error description line
        error_matches = re.findall(error_pattern, error_log)
        if error_matches:
            raw_error = error_matches[-1]
        else:
            # Fallback signature parser if standard traceback structure differs
            last_line = error_log.strip().split("\n")[-1]
            if last_line:
                raw_error = last_line

        logger.info(f"[AGENT: ANALYZER] Decoded target: {target_file} at line {line_number}")
        return {
            "exception_type": raw_error.split(":")[0].strip() if ":" in raw_error else "RuntimeError",
            "target_file": target_file,
            "line_number": line_number,
            "raw_error": raw_error
        }

    except Exception as e:
        logger.error(f"[AGENT: ANALYZER] Local tracing component failure: {e}")
        
    return {"error": "Failed to extract log context cleanly."}