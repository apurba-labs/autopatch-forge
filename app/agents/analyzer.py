import re

from app.core.config import logger


async def analyze_log_payload(error_log: str) -> dict:
    """
    Deterministic Trace Analyzer

    Extracts structured metadata from Python traceback logs.
    This component performs no AI inference.
    """

    logger.info("[ANALYZER] Parsing traceback...")

    result = {
        "exception_type": "RuntimeError",
        "target_file": None,
        "line_number": None,
        "raw_error": None,
    }

    try:
        # ----------------------------------------------------------
        # Find all traceback frames
        # Example:
        # File "/app/main.py", line 42, in <module>
        # ----------------------------------------------------------
        frame_pattern = re.compile(
            r'File\s+[\'"](?P<file>.+?)[\'"]\s*,\s*line\s+(?P<line>\d+)',
            re.MULTILINE,
        )

        frames = list(frame_pattern.finditer(error_log))

        if frames:
            last_frame = frames[-1]

            result["target_file"] = last_frame.group("file")
            result["line_number"] = int(last_frame.group("line"))

        # ----------------------------------------------------------
        # Find the exception line
        # Example:
        # ModuleNotFoundError: No module named 'httpx'
        # ----------------------------------------------------------
        exception_pattern = re.compile(
            r'(?P<exception>[A-Za-z_][A-Za-z0-9_]*Error):\s*(?P<message>.+)'
        )

        exception_match = exception_pattern.search(error_log)

        if exception_match:
            result["exception_type"] = exception_match.group("exception")
            result["raw_error"] = exception_match.group(0)
        else:
            lines = [line.strip() for line in error_log.splitlines() if line.strip()]
            if lines:
                result["raw_error"] = lines[-1]

        # ----------------------------------------------------------
        # Apply safe defaults
        # ----------------------------------------------------------
        result["target_file"] = (
            result["target_file"] or "unknown"
        )

        result["line_number"] = (
            result["line_number"] or 0
        )

        result["raw_error"] = (
            result["raw_error"] or "Unknown runtime error."
        )

        logger.info(
            "[ANALYZER] %s detected in %s:%s",
            result["exception_type"],
            result["target_file"],
            result["line_number"],
        )

        return result

    except Exception as e:
        logger.exception("[ANALYZER] Failed to parse traceback: %s", e)

        return {
            "exception_type": "ParserError",
            "target_file": "unknown",
            "line_number": 0,
            "raw_error": str(e),
        }