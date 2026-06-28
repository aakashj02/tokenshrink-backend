import tiktoken

class TokenCounterService:
    @staticmethod
    def count_tokens(text: str, model_encoding: str = "cl100k_base") -> int:
        """
        Calculates the exact token weight of a given string snippet.
        """
        try:
            encoding = tiktoken.get_encoding(model_encoding)
        except ValueError:
            encoding = tiktoken.get_encoding("cl100k_base")
            
        return len(encoding.encode(text))

    @classmethod
    def calculate_savings(
        cls, 
        original_tokens: int, 
        optimized_tokens: int, 
        price_per_million: float
    ) -> float:
        """Calculates precise financial differences between raw and stripped strings."""
        tokens_saved = max(0, original_tokens - optimized_tokens)
        savings = (tokens_saved / 1_000_000) * price_per_million
        return round(savings, 7)