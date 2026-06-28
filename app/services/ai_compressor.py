from openai import AsyncOpenAI
from app.core.config import settings
import logging

# Set up logging so we can see errors in the Render dashboard
logger = logging.getLogger(__name__)

class AICompressorService:
    def __init__(self):
        # Increased timeout and retry logic for cloud reliability
        self.client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            timeout=60.0,
            max_retries=3
        )
        self.model_name = "gpt-4o-mini"

    async def compress_prompt(self, user_prompt: str) -> str:
        """
        Transmits raw data to ChatGPT to strip semantic bloat 
        while preserving the core instruction.
        """
        system_instruction = (
            "You are an expert prompt compilation engine. "
            "Your objective is to rewrite the user input to be as concise as possible "
            "while preserving 100% of the underlying semantic intent. "
            "Return EXCLUSIVELY the raw optimized prompt."
        )

        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3 # Lower temperature for more consistent, concise output
            )
            
            optimized_text = response.choices[0].message.content.strip()
            return optimized_text

        except Exception as e:
    # Instead of just logging, raise the error so the API returns a 500
            logger.error(f"OpenAI API Error: {str(e)}")
            raise e  # <--- This is the crucial change