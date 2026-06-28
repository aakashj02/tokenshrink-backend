from openai import AsyncOpenAI
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# 1. MOVE THIS HERE: Constants should be at the top of the file
SYSTEM_INSTRUCTION = (
    "ACT AS A DETERMINISTIC PROMPT COMPRESSION ENGINE.\n\n"
    "YOUR SOLE OBJECTIVE: Rewrite the input prompt for maximum token efficiency and information density.\n\n"
    "STRICT OPERATIONAL RULES:\n"
    "1. OUTPUT FORMAT: Return ONLY the optimized text. ABSOLUTELY NO introductory phrases, "
    "no 'Here is the prompt', no conversational filler, no explanations, no meta-talk.\n"
    "2. LOGIC PRESERVATION: Retain 100% of the intent, logic, constraints, and instructions of the original.\n"
    "3. PRESERVATION TAGS: If the input contains text wrapped in <preserve> tags, "
    "copy that text EXACTLY as-is. DO NOT alter, optimize, or shorten text within <preserve> tags.\n"
    "4. COMPRESSION STRATEGY: Use atomic vocabulary, remove redundancies, and prune all pleasantries.\n"
    "5. FAILURE MODE: If the prompt is already optimal, return it unchanged.\n\n"
    "ANY RESPONSE THAT IS NOT THE OPTIMIZED PROMPT ITSELF WILL BE CONSIDERED A SYSTEM FAILURE."
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