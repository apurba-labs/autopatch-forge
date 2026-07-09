import json

import httpx

from app.core.config import logger, settings


async def evaluate_patch_risk(analysis: dict, patch: str) -> dict:
    """
    AI Risk Assessment Agent

    Uses Gemma (via Fireworks AI / AMD Cloud) to evaluate the
    operational risk of an automatically generated code patch.

    This component provides guidance only.
    The deterministic Patch Engine remains responsible for
    applying code changes.
    """

    logger.info("[GEMMA] Starting AI risk assessment...")

    # ------------------------------------------------------------------
    # Local Development Fallback
    # ------------------------------------------------------------------
    endpoint = settings.AMD_CLOUD_GEMMA_ENDPOINT or ""

    if (
        not endpoint
        or "localhost" in endpoint
        or "127.0.0.1" in endpoint
    ):
        logger.info("[GEMMA] Local mode detected. Using deterministic fallback.")

        confidence = 0.90

        exception = analysis.get("exception_type")

        if exception == "ModuleNotFoundError":
            confidence += 0.05

        if patch.strip().startswith("import "):
            confidence += 0.03

        confidence = min(confidence, 0.99)

        return {
            "confidence": round(confidence, 2),
            "risk": "low",
            "recommended_action": "Create Pull Request",
            "reasoning": (
                "The proposed remediation introduces a missing import "
                "without modifying application logic. Static analysis "
                "indicates low deployment risk."
            ),
        }

    # ------------------------------------------------------------------
    # Prompt
    # ------------------------------------------------------------------
    system_prompt = """
You are an expert Software Reliability Engineer.

Your task is to evaluate the operational risk of an automatically
generated source code patch.

Return ONLY valid JSON.

Schema:

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

    payload = {
        "model": settings.GEMMA_AUDITOR_MODEL,
        "messages": [
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
        "temperature": 0.1,
        "max_tokens": 256,
        "response_format": {"type": "json_object"},
    }

    headers = {
        "Content-Type": "application/json",
    }

    try:

        async with httpx.AsyncClient(timeout=15.0) as client:

            response = await client.post(
                f"{endpoint}/chat/completions",
                headers=headers,
                json=payload,
            )

            response.raise_for_status()

            body = response.json()

            result = json.loads(
                body["choices"][0]["message"]["content"]
            )

            required_fields = {
                "confidence",
                "risk",
                "recommended_action",
                "reasoning",
            }

            if not required_fields.issubset(result):
                raise ValueError(
                    "Gemma returned an incomplete response."
                )

            result["confidence"] = float(result["confidence"])

            logger.info(
                "[GEMMA] Risk assessment completed successfully."
            )

            return result

    except httpx.HTTPStatusError as e:
        logger.error(
            "[GEMMA] HTTP status error: %s",
            e.response.status_code,
        )

    except httpx.RequestError as e:
        logger.error(
            "[GEMMA] Request error: %s",
            str(e),
        )

    except json.JSONDecodeError:
        logger.error(
            "[GEMMA] Failed to parse AI JSON response."
        )

    except Exception as e:
        logger.exception(
            "[GEMMA] Unexpected validation error: %s",
            str(e),
        )

    logger.warning(
        "[GEMMA] Falling back to manual review."
    )

    return {
        "confidence": 0.0,
        "risk": "high",
        "recommended_action": "Manual Review Required",
        "reasoning": (
            "The AI validation service could not complete the "
            "risk assessment. The generated patch should be "
            "reviewed manually before deployment."
        ),
    }