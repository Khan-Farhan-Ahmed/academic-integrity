# PROOFly: Hackathon Quick Reference

## 1. Project Pitch
**"AI detectors are broken.** They output unexplainable percentages (e.g., '99% AI'), leading to false accusations and ruined trust. PROOFly replaces black-box detection with an **investigative platform**. We provide transparent, mathematically verifiable evidence (like sentence uniformity variance and semantic parity mapping) to empower educators with actionable data, not just an arbitrary score."

## 2. Tech Stack
- **Frontend**: Next.js (App Router), TypeScript, Tailwind CSS, shadcn/ui, Vercel
- **Backend**: Python, FastAPI, Pytest, Docker, Render/Cloud Run
- **ML / AI**: Gemini 3.8 Flash (Explanations), `gemini-embedding-2` (Vectors), PyMuPDF
- **Database**: Supabase PostgreSQL, `pgvector`, Row Level Security (RLS)

## 3. Architecture & Pipeline
1. **Extraction**: PDF/DOCX to text. Max 25,000 words.
2. **Feature Math**: Calculates vocabulary density and sentence length standard deviations.
3. **Embeddings**: Text chunks converted to 768-dim semantic vectors.
4. **Signal Generation**: Evaluates fingerprint deviation, source similarity, and paraphrase lexical gaps.
5. **Evidence Engine**: Deterministically weighs signals into Risk (0-100) and Confidence metrics.
6. **Explanation**: Gemini converts the JSON Evidence graph into a non-accusatory summary.
7. **Storage**: Complete historical state saved securely in Supabase.

## 4. Demo Flow
1. **Show Login**: Direct attention to the slogan: *"Don't just detect suspicious writing. Show the evidence behind it."*
2. **Dashboard**: Highlight the High/Medium/Low risk distribution charts.
3. **Upload Process**: Upload the AI-generated demo PDF. Explain the ML steps occurring synchronously.
4. **Investigation Report**: Open the result. Point out the Evidence Cards and Gemini's neutral summary.
5. **Highlighting**: Click an Evidence Card. Show the judges how the exact offending span is visually highlighted in the source document.

## 5. Judge Q&A (25 Core Answers)

1. **How do you detect AI?** We use deterministic math (sentence uniformity variance, lexical density) combined with semantic embeddings, aggregated by an Evidence Engine.
2. **How do you reduce false positives?** We use a "Confidence" metric and a "Writing Fingerprint" baseline. If a student naturally writes robotically, their baseline accounts for it.
3. **Why not use an LLM as the detector?** LLMs hallucinate false positives. We use math for detection and the LLM purely for summarization.
4. **Why Gemini?** Gemini 3.8 Flash is incredibly fast, and `gemini-embedding-2` natively supports high-dimensional semantic clustering.
5. **Why embeddings?** They let us compare the *meaning* of a sentence, defeating basic synonym-swapping paraphrasers.
6. **How does fingerprinting work?** We average linguistic metrics from a student's past submissions and measure the standard deviation of new submissions against it.
7. **How is plagiarism different from AI detection?** Plagiarism is lexical (exact word copy). AI detection is stylistic (variance/uniformity). Paraphrasing is high semantic overlap but low lexical overlap. We detect all three.
8. **Can your system prove cheating?** No. We provide *investigative evidence*, not definitive proof. The instructor makes the final call.
9. **What happens with short text?** The system flags it with "Low Confidence", as texts <50 words lack statistical weight.
10. **What happens if a student paraphrases AI output?** Our Paraphrase analyzer catches high semantic similarity paired with low lexical matching.
11. **How do you evaluate accuracy?** We run an automated Pytest evaluation script tracking False Positive Rates (FPR), optimizing heavily to protect human writers.
12. **What are the limitations?** False positives exist, it requires a baseline for fingerprinting, and source-matching requires the teacher to supply the source text.
13. **Why is this better than existing detectors?** Existing tools output a single, unexplainable percentage. We output the exact evidence and the rationale behind it.
14. **How would you scale this?** Move the synchronous FastAPI orchestrator into a Celery/Redis message queue for asynchronous processing.
15. **How do you protect student data?** Supabase Row Level Security (RLS) ensures instructors can only query their own mapped `student_id` records.
16. **Why Next.js?** Server Components easily bridge the gap between our secure database and the dynamic client UI.
17. **Did you train your own model?** No, we built a deterministic heuristic engine layered over foundation vector models to ensure explainability.
18. **Why FastAPI?** Native async support and seamless Pydantic validation for heavily structured JSON inputs.
19. **What if the Gemini API goes down?** The backend safely catches timeouts and degrades gracefully, returning a pre-written static summary so the app never crashes.
20. **Can it handle massive files?** Yes, we truncate document processing at 25,000 words to prevent token exhaustion.
21. **Do you support DOCX/PDF?** Yes, using `pymupdf` and `python-docx` we sanitize text blocks while preserving paragraph breaks.
22. **What's your biggest technical achievement?** Synthesizing distinct NLP pipelines (heuristics, vector search, LLM generation) into a single, lightning-fast synchronous API response.
23. **How does the frontend highlighter work?** The backend explicitly returns exact `matched_text` spans, which the React UI maps and wraps in HTML `<mark>` tags dynamically.
24. **Did you fake the dashboard data?** No. Everything fetched on the Next.js frontend is actively querying real Supabase SQL tables.
25. **What's the next feature?** Canvas/LMS integration via LTI standard to automatically analyze assignments on submission.

## 6. Local Run Commands
**Backend:**
```bash
export GEMINI_API_KEY="..."
export SUPABASE_URL="..."
export SUPABASE_KEY="..."
.\.venv\Scripts\activate
uvicorn backend.main:app --reload
```
**Frontend:**
```bash
cd frontend
npm run dev
```
**Seeder:**
```bash
python scripts/seed_demo.py
```
