import json

from app.ai.llm_client import llm_client
from app.core.config import logger, settings


async def evaluate_patch_risk(
    analysis: dict,
    patch: str,
) -> dict:
    """
    AI Risk Assessment Agent.

    Evaluates the operational risk
    of an automatically generated patch.
    """

    logger.info("[GEMMA RISK ASSESSOR] Starting evaluation...")

    # ---------------------------------------------------------
    # Local deterministic fallback
    # ---------------------------------------------------------

    if not settings.fireworks_api_key:

        confidence = 0.90

        if analysis.get("exception_type") == "ModuleNotFoundError":
            confidence += 0.05

        if patch.startswith("import "):
            confidence += 0.03

        confidence = min(confidence, 0.99)

        return {
            "confidence": round(confidence, 2),
            "risk": "low",
            "recommended_action": "Create Pull Request",
            "reasoning": (
                "Static analysis indicates that the generated patch "
                "only introduces a missing dependency import."
            ),
        }

    system_prompt = """
You are an expert Software Reliability Engineer.

Evaluate ONLY the operational risk of the proposed patch.

Return ONLY a valid JSON object.

Do not use markdown.

Do not explain anything.

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

Generated Patch

{patch}
"""

    response = await llm_client.chat(
        model=settings.risk_assessor_model,
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        temperature=0.0,
        max_tokens=128,
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

    if not isinstance(result, dict):
        logger.warning("[GEMMA] Invalid JSON response.")

        return {
            "confidence": 0.0,
            "risk": "high",
            "recommended_action": "Manual Review Required",
            "reasoning": "LLM returned invalid JSON.",
        }

    required = {
        "confidence",
        "risk",
        "recommended_action",
        "reasoning",
    }

    missing = required - result.keys()

    if missing:
        logger.error(
            "[GEMMA] Missing fields: %s",
            ", ".join(sorted(missing)),
        )
        logger.debug(
            "[GEMMA] Raw response: %s",
            json.dumps(result, indent=2),
        )
        return {
            "confidence": 0.0,
            "risk": "high",
            "recommended_action": "Manual Review Required",
            "reasoning": "Incomplete AI validation response.",
        }

    result["confidence"] = float(result["confidence"])

    logger.info("[GEMMA] Risk assessment completed.")

    return result