# Academic Integrity Investigation & Risk Analysis System (Proofly)

## Tech Stack
- **Frontend**: Next.js + TypeScript + Tailwind CSS + shadcn/ui
- **Backend**: Python + FastAPI
- **Database/Storage**: Supabase (PostgreSQL)
- **ML/AI**: Python, scikit-learn, spaCy, Gemini API

## Project Structure
- `frontend/` - Next.js React application
- `backend/` - FastAPI python server
- `ml/` - Machine learning models and analysis tools
- `docs/` - Documentation
- `tests/` - Tests

## Local Development Setup

### 1. Environment Variables
Copy `.env.example` to `.env` and fill in the values:
```bash
cp .env.example .env
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
The frontend will be available at `http://localhost:3000`.

### 3. Backend Setup
Make sure you have Python installed.

```bash
# Create and activate virtual environment
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Unix or MacOS:
source .venv/bin/activate

# Install requirements
pip install -r backend/requirements.txt

# Run the server
uvicorn backend.main:app --reload --port 8000
```
The API will be available at `http://localhost:8000` with the health check at `/api/health`.

API Documentation (Swagger UI) is available at `http://localhost:8000/docs`.
