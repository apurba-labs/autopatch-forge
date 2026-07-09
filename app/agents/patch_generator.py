import json

import httpx

from app.core.config import logger, settings


async def generate_patch(analysis: dict) -> dict:
    """
    Hybrid Patch Planning Agent

    Strategy

    1. Known failures
       -> deterministic rules (0 AI tokens)

    2. Unknown failures
       -> Fireworks / Gemma inference

    Returns

    {
        operation,
        content,
        reason
    }
    """

    logger.info("[PATCH PLANNER] Selecting remediation strategy...")

    exception = analysis.get("exception_type", "")

    # ---------------------------------------------------------
    # Rule-based strategies
    # ---------------------------------------------------------
    strategies = {
        "ModuleNotFoundError": {
            "operation": "insert_import",
            "content": "import httpx",
            "reason": "Missing dependency import detected.",
        },
        "ImportError": {
            "operation": "insert_import",
            "content": "import httpx",
            "reason": "Import resolution failure detected.",
        },
    }

    if exception in strategies:

        logger.info(
            "[PATCH PLANNER] Using deterministic strategy."
        )

        return strategies[exception]

    # ---------------------------------------------------------
    # AI Fallback
    # ---------------------------------------------------------

    logger.info(
        "[PATCH PLANNER] Escalating to Fireworks AI..."
    )

    if not settings.FIREWORKS_API_KEY:

        logger.warning(
            "[PATCH PLANNER] FIREWORKS_API_KEY missing."
        )

        return {
            "operation": "manual_review",
            "content": "",
            "reason": "AI inference unavailable.",
        }

    prompt = f"""
You are an expert Python software engineer.

Exception

{json.dumps(analysis, indent=2)}

Generate ONLY a JSON object.

Schema

{{
    "operation":"insert_import|replace|insert|manual_review",
    "content":"python code",
    "reason":"short explanation"
}}
"""

    payload = {
        "model": settings.LOG_PARSER_MODEL,
        "messages": [
            {
                "role": "system",
                "content": "Return ONLY JSON."
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        "temperature": 0.1,
        "max_tokens": 128,
        "response_format": {
            "type": "json_object"
        },
    }

    headers = {
        "Authorization": f"Bearer {settings.FIREWORKS_API_KEY}",
        "Content-Type": "application/json",
    }

    try:

        async with httpx.AsyncClient(timeout=10.0) as client:

            response = await client.post(
                f"{settings.FIREWORKS_BASE_URL}/chat/completions",
                headers=headers,
                json=payload,
            )

            response.raise_for_status()

            result = json.loads(
                response.json()["choices"][0]["message"]["content"]
            )

            logger.info(
                "[PATCH PLANNER] AI strategy generated."
            )

            return result

    except Exception as e:

        logger.exception(
            "[PATCH PLANNER] AI planning failed: %s",
            e,
        )

    return {
        "operation": "manual_review",
        "content": "",
        "reason": "AI planning failed.",
    }