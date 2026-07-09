import json

from app.ai.llm_client import llm_client
from app.core.config import logger, settings


async def generate_patch(analysis: dict) -> dict:
    """
    Hybrid Patch Planning Agent.

    Strategy

    1. Known failures
       -> Deterministic rules (0 AI tokens)

    2. Unknown failures
       -> Fireworks AI
    """

    logger.info("[GEMMA PATCH PLANNER] Selecting remediation strategy...")

    exception = analysis.get("exception_type", "")

    # ---------------------------------------------------------
    # Deterministic Strategies
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
        logger.info("[PATCH PLANNER] Using deterministic strategy.")
        return strategies[exception]

    # ---------------------------------------------------------
    # AI Strategy
    # ---------------------------------------------------------
    if not settings.FIREWORKS_API_KEY:
        logger.warning("[PATCH PLANNER] FIREWORKS_API_KEY not configured.")

        return {
            "operation": "manual_review",
            "content": "",
            "reason": "Fireworks AI unavailable.",
        }

    system_prompt = """
You are an expert Python software engineer.

Your job is to generate the smallest safe code patch.

Return ONLY valid JSON.

Schema:

{
    "operation":"insert_import|replace|insert|manual_review",
    "content":"python code",
    "reason":"short explanation"
}
"""

    user_prompt = f"""
Exception Analysis

{json.dumps(analysis, indent=2)}
"""

    try:

        response = await llm_client.chat(
            model=settings.PATCH_PLANNER_MODEL,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            max_tokens=128,
        )

        if not response["success"]:
            logger.warning("[PATCH PLANNER] AI planning failed.")

            return {
                "operation": "manual_review",
                "content": "",
                "reason": response["error"],
            }

        result = response["content"]

        required = {
            "operation",
            "content",
            "reason",
        }

        if not required.issubset(result):
            raise ValueError("Incomplete AI patch response.")

        logger.info("[PATCH PLANNER] AI patch generated successfully.")

        return result

    except Exception as e:
        logger.exception("[PATCH PLANNER] %s", str(e))

    return {
        "operation": "manual_review",
        "content": "",
        "reason": "AI patch generation failed.",
    }