import asyncio
import json

from fireworks import Fireworks

from app.core.config import logger, settings

class FireworksClient:
    """
    Shared Fireworks AI SDK wrapper.

    All AI agents (Patch Planner, Risk Assessor, Future Agents)
    should communicate with Fireworks through this client.
    """

    def __init__(self):
        self.client = Fireworks(api_key=settings.FIREWORKS_API_KEY)

    async def chat(
        self,
        *,
        model: str,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.1,
        max_tokens: int = 512,
    ) -> dict:
        """
        Executes a Fireworks Chat Completion using the official SDK.

        The Fireworks SDK is synchronous, so it is executed in a
        background thread to keep FastAPI endpoints non-blocking.
        """

        logger.info("[FIREWORKS] Calling model: %s", model)

        def _invoke():
            return self.client.chat.completions.create(
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

        try:
            response = await asyncio.to_thread(_invoke)

            content = response.choices[0].message.content.strip()

            logger.info("[FIREWORKS] Model completed successfully.")

            try:
                return json.loads(content)
            
            except json.JSONDecodeError:
                return {
                    "raw_response": content,
                }

        except Exception as e:
            logger.exception("[FIREWORKS] Inference failed: %s", str(e))
            raise

llm_client = FireworksClient()