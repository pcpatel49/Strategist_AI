# Strategist AI Agent

Strategist AI is a comprehensive college application advising platform, providing personalized academic, extracurricular, and college-planning guidance through an advanced AI assistant.

## Features
- **AI-Powered Strategist:** Get tailored college advice on classes, milestones, and extracurriculars from a personalized LLM Agent.
- **RAG & Private Memory:** Connects with Pinecone (and Mem0) to isolate context for user data and securely augment advice using your specific profile details.
- **Milestone & Activity Tracking:** Track up-to-date academics and activities directly on your dashboard.
- **Comprehensive Profiles:** Store SAT/ACT scores, target universities, and grades so the AI has context on your academic standing.
- **User Authentication:** Robust authentication with JWT, Email Verification, and Password Reset flow via FastAPI.

## Tech Stack
- **Backend:** Python + FastAPI + PostgreSQL (SQLAlchemy)
- **Frontend:** React + TypeScript + TailwindCSS + Vite
- **AI Infrastructure:** 
  - [Google Gemini / OpenAI] for the base LLM layer
  - Pinecone for vector storage / RAG
  - Mem0 for storing isolated per-user long-term memory

## Project Structure
- `api/`: FastAPI endpoint routes for dashboard, profile, documents, and chat.
- `auth/`: Authentication logic (JWT creation, registration, schemas).
- `database/`: PostgreSQL models, schema configuration, and alembic migrations.
- `memory/`: Mem0 isolated memory clients.
- `rag/`: Vector DB functionality with isolated Pinecone namespacing handling.
- `frontend/`: React codebase containing visual components and pages.

## Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+ (for Frontend)
- PostgreSQL Database
- Pinecone Account / API Key
- Mem0 API Key
- (Optional) Anthropic/OpenAI/Gemini API Key for the RAG agent

### Backend Setup
1. Create a `.env` file referencing `.env.example` in the root and fill out your variables:
    ```bash
    DATABASE_URL=postgresql://user:password@localhost/dbname
    SECRET_KEY=your_secret_key
    PINECONE_API_KEY=your_key
    MEM0_API_KEY=your_key
    ```
2. Set up the Python environment:
    ```bash
    pip install -r requirements.txt
    ```
3. Initialize Database Migrations:
    ```bash
    alembic upgrade head
    ```
4. Start the FastAPI backend:
    ```bash
    uvicorn api.main:app --reload --port 8000
    ```

### Frontend Setup
1. Navigate to the `frontend/` directory.
2. Install dependencies:
    ```bash
    npm install
    ```
3. Copy `.env.example` to `.env` inside `frontend/` if necessary.
4. Run the UI:
    ```bash
    npm run dev
    ```

## Usage
- Open `http://localhost:5173`
- Register a new account or log in.
- Set up your Academic Profile & Goals on the Profile page.
- Start chatting with the Strategist AI on the Chat page to receive an automated step-by-step game plan securely aligned to your personal data!
