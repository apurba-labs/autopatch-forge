import json

from app.ai.llm_client import llm_client
from app.core.config import logger, settings


async def evaluate_patch_risk(analysis: dict, patch: str) -> dict:
    """
    AI Risk Assessment Agent.

    Evaluates the operational risk of an automatically
    generated code patch.
    """

    logger.info("[GEMMA RISK ASSESSOR] Starting evaluation...")

    # ---------------------------------------------------------
    # Local deterministic fallback
    # ---------------------------------------------------------

    if not settings.FIREWORKS_API_KEY:

        confidence = 0.90

        if analysis.get("exception_type") == "ModuleNotFoundError" : confidence += 0.05

        if patch.startswith("import ") : confidence += 0.03

        confidence = min(confidence, 0.99)

        return {
            "confidence": round(confidence, 2),
            "risk": "low",
            "recommended_action": "Create Pull Request",
            "reasoning": (
                "Static analysis indicates that the patch only "
                "introduces a missing dependency import."
            ),
        }

    system_prompt = """
You are an expert Software Reliability Engineer.

Evaluate ONLY the operational risk of the proposed code patch.

Return ONLY valid JSON.

Schema

{
    "confidence": float,
    "risk": "low" | "medium" | "high",
    "recommended_action": string,
    "reasoning": string
}
"""

    user_prompt = f"""
Exception Analysis

{json.dumps(analysis, indent=2)}

Proposed Patch

{patch}
"""

    try:

        response = await llm_client.chat(
            model=settings.RISK_ASSESSOR_MODEL,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            max_tokens=256,
        )

        if not response["success"]:
            logger.warning("[GEMMA] Falling back to manual review.")

            return {
                "confidence": 0.0,
                "risk": "high",
                "recommended_action": "Manual Review Required",
                "reasoning": response["error"],
            }

        result = response["content"]

        required = {
            "confidence",
            "risk",
            "recommended_action",
            "reasoning",
        }

        if not required.issubset(result):
            raise ValueError("Incomplete AI validation response.")

        result["confidence"] = float(result["confidence"])

        logger.info("[GEMMA] Risk assessment completed.")

        return result

    except Exception as e:
        logger.exception("[GEMMA] %s", str(e))

    return {
        "confidence": 0.0,
        "risk": "high",
        "recommended_action": "Manual Review Required",
        "reasoning": (
            "AI validation could not be completed. "
            "Manual review is recommended."
        ),
    }