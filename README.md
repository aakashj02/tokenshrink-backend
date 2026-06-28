# TokenShrink Backend

TokenShrink is a high-performance FastAPI backend service designed to optimize user prompts for Large Language Models (LLMs). It reduces token consumption—and subsequently API costs—while employing an "LLM-as-a-Judge" validation layer to ensure that the core meaning and technical constraints of the original prompt are preserved.

## Architecture Overview

TokenShrink functions as an intelligent middleware layer between the end-user and the LLM provider:

1. **Request Reception:** FastAPI handles incoming `PromptRequest` payloads.
2. **Compression Service:** `AICompressorService` leverages `gpt-4o-mini` to perform semantic compression.
3. **Validation Layer:** A secondary "Judge" prompt compares the optimized output against the original to ensure 100% meaning preservation.
4. **Analytics:** `TokenCounterService` calculates real-time token savings and cost efficiencies.

## Project Structure

* `/app`: The FastAPI backend service.
* `/prompt_optimizer_extension`: The browser extension for direct API interaction.

## Getting Started

### Prerequisites

* Python 3.10+
* An OpenAI API Key

### Installation

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/aakashj02/tokenshrink-backend.git](https://github.com/aakashj02/tokenshrink-backend.git)
   cd tokenshrink-backend