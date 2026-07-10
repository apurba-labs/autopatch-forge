import json

from app.ai.llm_client import llm_client
from app.core.config import logger, settings


async def generate_patch(analysis: dict) -> dict:
    """
    Hybrid Patch Planning Agent

    Strategy

    1. Known failures
       -> deterministic rules (0 AI tokens)

    2. Unknown failures
       -> Fireworks AI inference

    Returns

    {
        operation,
        content,
        reason
    }
    """

    logger.info("[GEMMA PATCH PLANNER] Selecting remediation strategy...")

    exception = analysis.get("exception_type", "")

    # ---------------------------------------------------------
    # Deterministic strategies
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
    # AI Fallback
    # ---------------------------------------------------------

    if not settings.fireworks_api_key:
        logger.warning("[PATCH PLANNER] FIREWORKS_API_KEY missing.")
        return {
            "operation": "manual_review",
            "content": "",
            "reason": "AI inference unavailable.",
        }

    system_prompt = """
You are an expert Python software engineer.

Generate the smallest SAFE code patch.

Return ONLY a valid JSON object.

Do not use markdown.

Do not explain anything.

Schema

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

    response = await llm_client.chat(
        model=settings.patch_planner_model,
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        temperature=0.0,
        max_tokens=128,
    )

    if not response["success"]:
        logger.warning("[PATCH PLANNER] AI unavailable.")

        return {
            "operation": "manual_review",
            "content": "",
            "reason": response["error"],
        }

    result = response["content"]

    if not isinstance(result, dict):
        logger.warning("[PATCH PLANNER] Invalid JSON response.")
        return {
            "operation": "manual_review",
            "content": "",
            "reason": "LLM returned invalid JSON.",
        }

    required = {
        "operation",
        "content",
        "reason",
    }

    missing = required - result.keys()

    if missing:

        logger.error(
            "[PATCH PLANNER] Missing fields: %s",
            ", ".join(sorted(missing)),
        )

        return {
            "operation": "manual_review",
            "content": "",
            "reason": "Incomplete AI response.",
        }

    logger.info("[PATCH PLANNER] AI strategy generated.")

    return result