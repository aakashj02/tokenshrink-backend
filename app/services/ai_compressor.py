from openai import AsyncOpenAI
from app.core.config import settings

class AICompressorService:
    def __init__(self):
        # Configure a relaxed timeout setting to handle slower network drops
        self.client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            timeout=30.0  # Increased timeout parameter from default
        )
        self.model_name = "gpt-4o-mini"

    async def compress_prompt(self, user_prompt: str) -> str:
        """
        Transmits raw data to ChatGPT with system parameters designed to 
        strip semantic bloat while protecting programmatic structures.
        """
        system_instruction = (
            "You are an expert prompt compilation engine working as a low-latency gateway middleware. "
            "Your sole objective is to rewrite the user input to consume the minimum possible token weight "
            "while preserving 100% of the underlying semantic logic, programmatic variables, context guidelines, and constraints.\n\n"
            "Execution Protocols:\n"
            "1. Remove conversational bloat, introductory fluff, politeness markers, and redundant phrasing.\n"
            "2. Retain all explicit names, variable placeholders (e.g. {{variable}}), rules, and operational boundaries.\n"
            "3. Do not append explanatory text, conversational wrapping, notes, or markdown formatting blocks. "
            "Return exclusively the raw optimized prompt string."
        )

        try:
            # Execute chat completion natively inside OpenAI's async runtime loop
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1 # High determinism
            )
            
            if response.choices and response.choices[0].message.content:
                return response.choices[0].message.content.strip()
            return user_prompt
            
        except Exception as api_error:
            # Fail-safe mechanism: log securely and return base text rather than breaking down runtime execution
            print(f"[CRITICAL LOG] OpenAI API Network Interruption: {str(api_error)}")
            return user_prompt