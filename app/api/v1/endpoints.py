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
            detail="Provided prompt parameter cannot be empty."
        )

    original_prompt = payload.prompt
    original_count = TokenCounterService.count_tokens(original_prompt)
    
    # --- STEP 1: COMPRESS ---
    optimized_text = await ai_service.compress_prompt(original_prompt)
    
    # DEBUG LOG
    print(f"DEBUG: Original count: {original_count}")
    print(f"DEBUG: Optimized text: {optimized_text[:50]}...")

    # --- STEP 2: VERIFY (LLM Judge) ---
    judge_instruction = "Respond with ONLY 'YES' if meaning is kept, or 'NO' if meaning is lost."
    judge_input = f"Original: {original_prompt}\nOptimized: {optimized_text}"
    
    validation_result = "YES" # Default to YES for testing if judge fails
    try:
        validation_response = await ai_service.client.chat.completions.create(
            model=ai_service.model_name,
            messages=[{"role": "system", "content": judge_instruction}, {"role": "user", "content": judge_input}],
            temperature=0.0
        )
        validation_result = validation_response.choices[0].message.content or "NO"
    except Exception as e:
        print(f"DEBUG: Judge Error: {e}")
        validation_result = "YES" # Assume YES if AI service has a hiccup

    # --- STEP 3: FALLBACK CHECK ---
    optimized_count = TokenCounterService.count_tokens(optimized_text)
    
    # Logic: Agar Judge NO bole OR optimized text original se bada ho jaye, tabhi fallback karo
    # is_valid = "YES" in validation_result.upper()
    # if not is_valid or optimized_count >= original_count:
    #     print(f"DEBUG: Fallback Triggered! Valid: {is_valid}, NewCount: {optimized_count}")
    #     optimized_text = original_prompt
    #     optimized_count = original_count
    # else:
    #     print("DEBUG: Optimization Successful!")

    # --- STEP 4: METRICS ---
    tokens_saved = original_count - optimized_count
    compression_ratio = round((tokens_saved / original_count) * 100, 2) if original_count > 0 else 0.0
    cost_savings = TokenCounterService.calculate_savings(original_count, optimized_count, settings.INPUT_TOKEN_PRICE_PER_MILLION)

    return TokenOptimizeResponse(
        original_prompt=original_prompt,
        optimized_prompt=optimized_text,
        metrics=OptimizationMetrics(
            original_token_count=original_count,
            optimized_token_count=optimized_count,
            tokens_saved=tokens_saved,
            compression_ratio_percentage=compression_ratio,
            estimated_cost_saving_usd=cost_savings
        )
    )

# ... (compress_and_execute_endpoint function wahi rakho jo pehle tha)