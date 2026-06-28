from pydantic import BaseModel, Field

class TokenOptimizeRequest(BaseModel):
    prompt: str = Field(
        ..., 
        min_length=5, 
        description="The raw unoptimized prompt text to shrink.",
        examples=["Could you please be so kind as to write a clean and efficient Python function that computes the classic mathematical Fibonacci sequence? Thank you very much!"]
    )
    target_model: str = Field(
        default="gpt-4o-mini", 
        description="The underlying target model configuration to calculate tokens against.",
        examples=["gpt-4o-mini", "gpt-4o"]
    )

class OptimizationMetrics(BaseModel):
    original_token_count: int
    optimized_token_count: int
    tokens_saved: int
    compression_ratio_percentage: float
    estimated_cost_saving_usd: float

class TokenOptimizeResponse(BaseModel):
    original_prompt: str
    optimized_prompt: str
    metrics: OptimizationMetrics

class UnifiedRunResponse(BaseModel):
    optimized_prompt: str
    ai_response_text: str  # The actual answer from ChatGPT/Gemini
    metrics: OptimizationMetrics