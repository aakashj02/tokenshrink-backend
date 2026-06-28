from openai import AsyncOpenAI
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# 1. MOVE THIS HERE: Constants should be at the top of the file
SYSTEM_INSTRUCTION = (
    "You are a professional prompt optimization engine. Your goal is to rewrite prompts "
    "to be as short, dense, and token-efficient as possible.\n\n"
    "CRITICAL RULES:\n"
    "1. Maintain 100% of the original meaning, intent, and technical constraints.\n"
    "2. If you see text wrapped inside <preserve>...</preserve> tags, you MUST keep "
    "that exact text intact without changing a single word.\n"
    "3. Remove all conversational fluff, pleasantries, and meta-commentary."
)

class AICompressorService:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            timeout=60.0,
            max_retries=3
        )
        self.model_name = "gpt-4o-mini"

    async def compress_prompt(self, user_prompt: str) -> str:
        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    # 2. Now it references the global constant
                    {"role": "system", "content": SYSTEM_INSTRUCTION},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.0
            )
            
            optimized_text = response.choices[0].message.content.strip()
            return optimized_text

        except Exception as e:
            logger.error(f"OpenAI API Error: {str(e)}")
            raise e