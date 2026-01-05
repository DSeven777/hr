# Intelligent Recruitment System (AI Recruitment)

A LangChain-based intelligent recruitment system implementing Resume Parsing, Job Description Analysis, and AI-driven Candidate Matching.

## 🚀 Features

- **Resume Parsing**: Extract structured data (Skills, Experience, Education) from unstructured text.
- **JD Analysis**: Parse Job Descriptions into structured requirements.
- **Intelligent Matching**: Evaluate candidates against JDs with detailed scoring and reasoning.
- **Architecture**: Strictly follows Domain-Driven Design (DDD) with 5-layer architecture.

## 🛠️ Tech Stack

- **Core**: Python 3.11+
- **AI Framework**: LangChain 0.3.x
- **LLM**: OpenAI (GPT-4 Turbo recommended)
- **Vector DB**: FAISS (Local)
- **API**: FastAPI
- **Validation**: Pydantic v2

## 📂 Project Structure

```
src/
├── domain/     # Pydantic Models (Resume, Job, MatchResult)
├── prompt/     # Jinja2 Prompt Templates
├── chain/      # LangChain Runnables (Single Responsibility)
├── service/    # Business Logic Orchestration
├── infra/      # Infrastructure Adapters (LLM, VectorStore)
└── main.py     # FastAPI Entry Point
```

## ⚡ Quick Start

### 1. Prerequisites
- Python 3.10 or higher
- OpenAI API Key

### 2. Installation
```bash
# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration
Copy `.env.example` to `.env` and configure your API key:
```bash
cp .env.example .env
# Edit .env file
```

### 4. Run Server
```bash
# Run with uvicorn directly
uvicorn src.main:app --reload

# Or via python module
python -m src.main
```

## 📝 API Usage

- **Parse Resume**: `POST /api/v1/resume/parse`
- **Parse JD**: `POST /api/v1/job/parse`
- **Match**: `POST /api/v1/match`

Visit `http://localhost:8000/docs` for interactive API documentation.
