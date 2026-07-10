import json

from fireworks.client import AsyncFireworks

from app.core.config import logger, settings


class FireworksClient:
    """
    Shared Fireworks AI client.

    All AI agents communicate through this class.

    Returns a normalized response:

    {
        "success": bool,
        "content": dict | str | None,
        "error": str | None,
    }
    """

    def __init__(self):
        self.client = AsyncFireworks(
            api_key=settings.fireworks_api_key,
        )

    async def chat(
        self,
        *,
        model: str,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.1,
        max_tokens: int = 512,
    ) -> dict:

        logger.info(
            "[FIREWORKS] Calling model: %s",
            model,
        )

        try:

            response = await self.client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": user_prompt,
                    },
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )

            message = response.choices[0].message

            if message is None or message.content is None:

                logger.warning(
                    "[FIREWORKS] Empty model response."
                )

                return {
                    "success": False,
                    "content": None,
                    "error": "Model returned an empty response.",
                }

            content = message.content.strip()

            logger.info("[FIREWORKS] Model completed successfully.")

            try:
                parsed = json.loads(content)
                return {
                    "success": True,
                    "content": parsed,
                    "error": None,
                }

            except json.JSONDecodeError:
                logger.warning("[FIREWORKS] Response is not valid JSON.")
                return {
                    "success": True,
                    "content": content,
                    "error": None,
                }

        except Exception as e:
            logger.exception("[FIREWORKS] Inference failed: %s", str(e))

            return {
                "success": False,
                "content": None,
                "error": str(e),
            }


llm_client = FireworksClient()