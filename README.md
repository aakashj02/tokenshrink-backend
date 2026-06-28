# ⚡ TokenShrink Pro - Backend API

This is the backend service for the **TokenShrink Pro** browser extension. Built with FastAPI, this REST API is responsible for compressing LLM prompts and calculating real-time token footprint to help developers reduce API costs and optimize context windows.

---

## 🛠️ Tech Stack

- **Framework:** FastAPI, Uvicorn
- **AI Integration:** OpenAI API
- **Tokenization:** `tiktoken` (`cl100k_base`)
- **Environment Management:** `python-dotenv`

---

## 🚀 Project Architecture

- **`app/api/v1/`** – Contains the API routing and endpoints.
- **`app/services/ai_compressor.py`** – Handles the core logic for shrinking prompts using OpenAI's models.
- **`app/services/token_counter.py`** – Uses `tiktoken` to accurately calculate token usage before and after compression.
- **`app/schemas/prompt.py`** – Uses Pydantic models for strict request and response validation.

---

## ⚙️ Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/aakashj02/tokenshrink-backend.git
cd tokenshrink-backend
```

### 2. Create and activate a virtual environment

**Mac/Linux**

```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows**

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root and add:

```env
OPENAI_API_KEY=your_api_key_here
```

### 5. Run the development server

```bash
uvicorn app.main:app --reload
```