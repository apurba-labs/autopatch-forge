import httpx
import json
from app.core.config import settings, logger

async def analyze_log_payload(error_log: str) -> dict:
    """Agent 1: Decodes raw trace logs to extract broken parameters using Fireworks AI."""
    logger.info("[AGENT: ANALYZER] Routing trace log to Fireworks AI...")
    
    # Fallback if no API key is provided yet
    if not settings.FIREWORKS_API_KEY:
        logger.warning("[AGENT: ANALYZER] Missing FIREWORKS_API_KEY. Falling back to structured mock.")
        return {
            "exception_type": "ModuleNotFoundError",
            "target_file": "app/utils/helpers.py",
            "line_number": 14,
            "raw_error": "No module named 'httpx'"
        }
        
    prompt = (
        "You are an expert CI/CD DevOps debugging assistant. Analyze this runtime error log trace.\n"
        "Extract the raw parameters and return a strict JSON object with EXACTLY these keys:\n"
        "{\n"
        "  \"exception_type\": \"string\",\n"
        "  \"target_file\": \"string\",\n"
        "  \"line_number\": integer,\n"
        "  \"raw_error\": \"string\"\n"
        "}\n"
        f"Error Log:\n{error_log}"
    )
    
    headers = {
        "Authorization": f"Bearer {settings.FIREWORKS_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": settings.LOG_PARSER_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.0,
        "response_format": {"type": "json_object"}
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.FIREWORKS_BASE_URL}/chat/completions",
                headers=headers,
                json=payload,
                timeout=12.0
            )
            
            if response.status_code == 200:
                content = response.json()["choices"][0]["message"]["content"]
                return json.loads(content)
            else:
                logger.error(f"[AGENT: ANALYZER] LLM Route failed with status {response.status_code}: {response.text}")
    except Exception as e:
        logger.error(f"[AGENT: ANALYZER] Network connection failure to AI provider: {e}")
        
    return {"error": "Failed to parse log dynamically via LLM routing."}