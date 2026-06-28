from fastapi import APIRouter, HTTPException, status
from app.schemas.prompt import TokenOptimizeRequest, TokenOptimizeResponse, OptimizationMetrics, UnifiedRunResponse
from app.services.token_counter import TokenCounterService
from app.services.ai_compressor import AICompressorService
from app.core.config import settings

router = APIRouter()
ai_service = AICompressorService()

@router.post(
    "/optimize", 
    response_model=TokenOptimizeResponse, 
    status_code=status.HTTP_200_OK,
    summary="Optimize prompt strings for token efficiency"
)
async def optimize_prompt_endpoint(payload: TokenOptimizeRequest):
    if not payload.prompt.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Provided prompt parameter cannot be empty or whitespace."
        )

    original_prompt = payload.prompt
    original_count = TokenCounterService.count_tokens(original_prompt)
    
    # --- STEP 1: COMPRESS ---
    optimized_text = await ai_service.compress_prompt(original_prompt)

    # --- STEP 2: VERIFY (The LLM-as-a-Judge check) ---
    judge_instruction = (
        "You are a quality control system. Compare the Original Prompt and the Optimized Prompt. "
        "Does the Optimized version retain ALL technical requirements, variables, constraints, "
        "and the exact core meaning of the Original? Respond with exactly one word: YES or NO."
    )
    
    judge_input = f"Original:\n{original_prompt}\n\nOptimized:\n{optimized_text}"
    
    try:
        # Re-using your existing AI service to call the Judge
        validation_response = await ai_service.client.chat.completions.create(
            model=ai_service.model_name,
            messages=[
                {"role": "system", "content": judge_instruction},
                {"role": "user", "content": judge_input}
            ],
            temperature=0.0
        )
        validation_result = validation_response.choices[0].message.content or "NO"
    except Exception as e:
        # If the judge fails, default to NO to protect the user
        validation_result = "NO"

    # --- STEP 3: FALLBACK CHECK ---
    optimized_count = TokenCounterService.count_tokens(optimized_text)
    
    # We fallback to the original if the Judge says NO, if the API failed, or if it made the prompt longer
    if "YES" not in validation_result.upper() or not optimized_text or optimized_count > original_count:
        optimized_text = original_prompt
        optimized_count = original_count

    # --- STEP 4: METRICS & RETURN ---
    tokens_saved = original_count - optimized_count
    
    compression_ratio = 0.0
    if original_count > 0:
        compression_ratio = round((tokens_saved / original_count) * 100, 2)

    cost_savings = TokenCounterService.calculate_savings(
        original_tokens=original_count,
        optimized_tokens=optimized_count,
        price_per_million=settings.INPUT_TOKEN_PRICE_PER_MILLION
    )

    metrics_profile = OptimizationMetrics(
        original_token_count=original_count,
        optimized_token_count=optimized_count,
        tokens_saved=tokens_saved,
        compression_ratio_percentage=compression_ratio,
        estimated_cost_saving_usd=cost_savings
    )

    return TokenOptimizeResponse(
        original_prompt=original_prompt,
        optimized_prompt=optimized_text,
        metrics=metrics_profile
    )

@router.post(
    "/run", 
    response_model=UnifiedRunResponse,
    summary="Compress prompt and execute against the target AI model"
)
async def compress_and_execute_endpoint(payload: TokenOptimizeRequest):
    if not payload.prompt.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Provided prompt parameter cannot be empty or whitespace."
        )

    # Step 1: Profile and compress the prompt
    original_count = TokenCounterService.count_tokens(payload.prompt)
    optimized_text = await ai_service.compress_prompt(payload.prompt)
    optimized_count = TokenCounterService.count_tokens(optimized_text)
    
    if optimized_count > original_count or not optimized_text:
        optimized_text = payload.prompt
        optimized_count = original_count

    # Step 2: Pass the optimized prompt directly to the model for the actual answer
    try:
        response = await ai_service.client.chat.completions.create(
            model=ai_service.model_name,
            messages=[{"role": "user", "content": optimized_text}],
            temperature=0.7
        )
        ai_answer = response.choices[0].message.content or "" 
    except Exception as e:
        ai_answer = f"Failed to fetch response from model provider: {str(e)}"

    # Step 3: Compute analytics metrics
    tokens_saved = original_count - optimized_count
    compression_ratio = round((tokens_saved / original_count) * 100, 2) if original_count > 0 else 0.0
    cost_savings = TokenCounterService.calculate_savings(
        original_tokens=original_count,
        optimized_tokens=optimized_count,
        price_per_million=settings.INPUT_TOKEN_PRICE_PER_MILLION
    )

    return UnifiedRunResponse(
        optimized_prompt=optimized_text,
        ai_response_text=ai_answer,
        metrics=OptimizationMetrics(
            original_token_count=original_count,
            optimized_token_count=optimized_count,
            tokens_saved=tokens_saved,
            compression_ratio_percentage=compression_ratio,
            estimated_cost_saving_usd=cost_savings
        )
    )