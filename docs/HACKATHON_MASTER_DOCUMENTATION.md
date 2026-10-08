# PROOFly: Hackathon Master Documentation

## 1. Project Overview
- **Project name**: PROOFly
- **One-line description**: An investigative academic integrity platform that surfaces evidence of AI generation, source copying, and paraphrasing rather than just delivering a binary "cheated/not cheated" score.
- **Problem being solved**: Generic AI detectors provide black-box, unexplainable percentages that lead to false accusations and eroded student-teacher trust. 
- **Why this problem matters**: False positives in AI detection can ruin academic careers. Instructors need transparent evidence, not unexplainable verdicts, to have constructive conversations with students.
- **Target users**: University instructors, teaching assistants, and academic integrity boards.
- **Project goal**: Shift the paradigm from "AI Detection" to "Academic Investigation" by providing educators with explainable linguistic and statistical evidence.

---

## 2. Problem Statement
The current ecosystem relies heavily on black-box AI detectors (like GPTZero or Turnitin's AI score). These detectors look at text perplexity and burstiness, outputting a simple percentage (e.g., "99% AI"). 

**Limitations of simple AI detectors:**
- **Unexplainable:** They cannot tell an instructor *why* a text was flagged.
- **High False Positives:** They frequently flag non-native English speakers or neurodivergent students who naturally write with high uniformity.
- **Evidentiary Void:** A percentage score is not actionable proof in a disciplinary hearing. 

Because of this, institutions are disabling AI detectors. The problem isn't that students aren't cheating—it's that instructors lack the *evidence* required to confidently address it.

---

## 3. Our Proposed Solution
**Core message**: *"Don't just detect suspicious writing. Show the evidence behind it."*

We built an investigation-based approach. Instead of a single black-box model, PROOFly breaks down a submission into multiple independently verifiable vectors:
1. Does it match the student's historical writing fingerprint?
2. Does it contain unnatural semantic-to-lexical ratios indicative of AI paraphrasing tools?
3. Does it directly match reference materials?
4. Does it exhibit the extreme structural uniformity common in LLM outputs?

We aggregate these signals into a transparent **Evidence Engine**, calculate a Risk Score, and use an LLM (Gemini) purely to translate this statistical data into a neutral, non-accusatory report for the instructor.

---

## 4. Key Features
- **Document upload**: Instructors can upload student submissions via the dashboard.
- **PDF/DOCX/TXT extraction**: Extracts text while normalizing paragraphs. Max 25k words to protect API limits.
- **Linguistic feature extraction**: Analyzes vocabulary diversity, readability, structural markers, and sentence length variance.
- **AI writing signals**: Heuristic algorithms looking for extreme uniformity and repetitive transitional phrasing ("Furthermore", "In conclusion").
- **Writing fingerprint**: Establishes a baseline from a student's prior work and calculates stylistic deviation.
- **Source similarity**: Cosine similarity using vector embeddings against provided reference materials.
- **Paraphrase analysis**: Calculates the gap between semantic similarity (meaning) and lexical similarity (word overlap) to identify synonym-swapping.
- **Evidence engine**: A deterministic, configurable weighted system that aggregates signals into actionable evidence items.
- **Risk scoring**: Output (0-100) indicating the likelihood of academic integrity violations.
- **Confidence scoring**: Output indicating how reliable the system believes its own risk score is (based on text length, signal consistency).
- **Gemini explanation**: Uses Gemini 3.8 Flash strictly to translate the Evidence Engine's JSON into a readable, non-accusatory instructor summary.
- **Database**: Full PostgreSQL/Supabase schema persisting students, documents, and historical analysis results.
- **Authentication**: Role-based access control via Supabase JWTs.
- **Dashboard**: Next.js interface for managing students, viewing high-risk submissions, and navigating reports.
- **Investigation report**: A detailed, card-based UI breaking down each piece of evidence.
- **Evidence highlighting**: Cross-links evidence cards directly to highlighted spans in the document viewer.
- **Evaluation**: A Pytest-based benchmarking framework to track False Positive Rates (FPR) and F1 scores.
- **Deployment**: Configured for Vercel (Frontend) and Render/Cloud Run (FastAPI Docker).

---

## 5. Complete System Architecture

```text
      [Instructor User]
             │
             ▼
      [Next.js Frontend]  (UI, Auth, Dashboard, Highlighting)
             │
   (REST API / JWT Auth)
             │
             ▼
     [FastAPI Backend]    (Orchestrator, File Validation)
             │
             ▼
   [Document Processing]  (PDF/DOCX/TXT -> Clean Text, Max 25k Words)
             │
             ├─────────────────────────────────────────────────┐
             ▼                                                 ▼
  [Feature Extraction]                             [Gemini Embedding 2]
  (spaCy, NLTK-style stats)                        (768-dim vector chunks)
             │                                                 │
             ├───────────────────┬───────────────────┬─────────┘
             ▼                   ▼                   ▼
    [AI Writing Signals]  [Writing Fingerprint] [Paraphrase & Source Match]
             │                   │                   │
             └───────────────────┼───────────────────┘
                                 ▼
                         [Evidence Engine]
                 (Weighted Logic, Deduplication)
                                 │
             ┌───────────────────┴───────────────────┐
             ▼                                       ▼
    [Risk + Confidence]                    [Gemini 3.8 Flash]
    (0-100, LOW/MED/HIGH)                  (Explanation Layer)
             │                                       │
             └───────────────────┬───────────────────┘
                                 ▼
                     [Supabase PostgreSQL]
                  (Persistence, pgvector, RLS)
                                 │
                                 ▼
                     [Investigation Dashboard]
```

**Components:**
- **Frontend**: Handles user interactions and visually renders the highlighted report.
- **FastAPI**: The central nervous system routing data through the ML pipelines securely.
- **Document Processing**: Normalizes raw bytes into clean strings.
- **Feature Extraction**: Calculates baseline linguistics without calling external APIs.
- **Embeddings**: Converts text chunks to semantic vectors.
- **Analysis Engines**: Modular heuristic rules (AI signals, Fingerprint, Source Match).
- **Evidence Engine**: The deterministic decision-maker.
- **Explanation Layer**: The LLM that reads the Evidence Engine's structured JSON and writes a human-readable summary.
- **Supabase**: The source of truth for historical records.

---

## 6. Complete End-to-End Data Flow
1. **File Upload**: The instructor uploads a `.pdf` to the Next.js frontend, specifying the `student_id`.
2. **Network Request**: Frontend wraps the file and the Supabase JWT into a `multipart/form-data` POST request to `/api/analysis/run`.
3. **Validation**: FastAPI verifies the file size (<10MB), MIME type, and ensures the `student_id` is owned by the authenticated instructor.
4. **Extraction**: `pymupdf` parses the PDF. Text >25,000 words is truncated.
5. **Feature Extraction**: Sentence boundaries and lexical stats are computed.
6. **AI Signals**: Text is checked for standard deviation in sentence length and AI "transition word" density.
7. **Embeddings Generation**: The text is chunked and sent to Gemini to retrieve `gemini-embedding-2` vectors.
8. **Source/Paraphrase Analysis**: Vectors are compared against any reference vectors via cosine similarity.
9. **Evidence Engine**: Independent signals are passed to the engine. It applies weights and generates a list of `EvidenceItem` objects, calculating a `Risk Score` and `Confidence`.
10. **Gemini Explanation**: The Engine's JSON is passed to Gemini 3.8 with strict instructions to generate a neutral summary.
11. **Persistence**: The FastAPI backend upserts the document, extracts, evidence, and report into Supabase PostgreSQL.
12. **Response**: A complete JSON graph is returned to the frontend.
13. **Investigation Report**: Next.js renders the data, rendering colored `<mark>` tags over matching text chunks in the document viewer.

---

## 7. Technology Stack

| Technology | Purpose | Why it was selected | Where it is used |
|------------|---------|---------------------|------------------|
| **Next.js** | Frontend Framework | Fast SSR, easy routing, server actions | Entire UI |
| **TypeScript** | Type Safety | Prevents runtime bugs during rapid dev | Frontend UI |
| **Tailwind CSS** | Styling | Rapid, consistent UI design | Frontend UI |
| **shadcn/ui** | UI Components | Accessible, customizable pre-built components | Dashboard, Cards, Tables |
| **Python** | ML/Backend Language | Standard for data science and text processing | Entire Backend |
| **FastAPI** | Backend Framework | High performance, async, auto-docs | Backend Orchestrator |
| **Gemini API** | Embeddings & LLM | High context window, fast `flash` models | Paraphrasing, Explanations |
| **Supabase** | DB & Auth | RLS security, rapid PostgreSQL setup | Auth, Data Persistence |
| **pgvector** | Vector Search | Native PostgreSQL similarity search | (Configured in Schema) |
| **Vercel** | Frontend Hosting | Zero-config Next.js deployment | Production URL |
| **Cloud Run/Render** | Backend Hosting | Easy Docker container orchestration | Python API |
| **PyMuPDF** | PDF Parsing | Robust, handles complex academic PDFs | Extraction module |
| **python-docx** | DOCX Parsing | Native word doc parsing | Extraction module |

---

## 8. Backend Architecture
- **Structure**: Modularized into `/api` (routers), `/db` (Supabase connections), `/ml` (AI logic), and `/services` (Extraction).
- **Validation**: Strict Pydantic models for inputs and outputs. Max file size (10MB) limits.
- **Error Handling**: Wrapped in explicit `try/except` blocks. If Gemini rate-limits, it degrades gracefully to a fallback JSON report rather than crashing 500.
- **Authentication**: FastAPI `Depends(get_instructor_user)` decodes the Supabase JWT.

**Key API Endpoints:**

| METHOD | PATH | PURPOSE | INPUT | OUTPUT |
|--------|------|---------|-------|--------|
| `POST` | `/api/analysis/run` | Main pipeline orchestrator | `file`, `student_id`, JWT | Complete `OrchestratorResult` JSON |
| `POST` | `/api/documents/upload` | Basic extraction (Health test) | `file` | `DocumentExtractionResponse` |
| `GET` | `/api/health` | Deployment liveness check | None | `{"status": "ok"}` |

---

## 9. Frontend Architecture
- **Structure**: App Router `src/app/(dashboard)`.
- **Pages**: `/dashboard` (stats), `/submissions` (upload/table), `/students` (directory), `/reports` (history).
- **Components**: `ReportViewer` isolates complex highlighting logic. `UploadSubmissionForm` handles `FormData` state and JWT fetching.
- **State Handling**: standard React `useState/useMemo` combined with Next.js Server Component data fetching.
- **API Communication**: The frontend fetches historical data directly via Supabase SSR, but actively talks to the FastAPI Python backend for heavy ML document processing.

---

## 10. Machine Learning / NLP Architecture

**1. Linguistic Features (`ml.features`)**
- *What it is*: Statistical mapping of vocabulary and sentences.
- *Why we use it*: Forms the baseline mathematical signature of a text.
- *Processing*: Calculates distinct word ratios, standard deviation of sentence lengths.

**2. AI-Writing Signals (`ml.ai_signals`)**
- *What it is*: Heuristics targeting LLM behavior.
- *Why we use it*: LLMs naturally regress to the mean, creating artificially perfect uniformity.
- *Processing*: Checks for variance < 0.25 (highly robotic), and counts transitions like "Furthermore, In conclusion".

**3. Embeddings (`ml.embeddings`)**
- *What it is*: `gemini-embedding-2` vector encoding.
- *Why we use it*: To understand the *meaning* of a sentence, not just its exact words.
- *Processing*: Chunks text into manageable overlaps, returns 768-dim floats.

**4. Source Similarity (`ml.source_similarity`)**
- *What it is*: Cosine similarity matching.
- *Processing*: Returns a flag if `cosine(chunk, reference) > 0.85`.

**5. Paraphrase Signals (`ml.paraphrase`)**
- *What it is*: Comparing semantics vs lexicons.
- *Processing*: If two texts have high semantic similarity (vectors > 0.85) but low lexical similarity (Jaccard < 0.4), it indicates someone aggressively used a thesaurus or an AI rewriter to hide plagiarism.

**6. Evidence Aggregation (`ml.evidence_engine`)**
- *What it is*: Weighted deterministic decision tree.
- *Processing*: Maps arbitrary ML scores into a structured array of actionable `EvidenceItem` objects.

*Note: We strictly do not claim these techniques mathematically prove AI authorship. They are statistical deviations flagging behavior warranting human review.*

---

## 11. AI Detection Methodology
We explicitly separate concepts to maintain instructor trust:
- **Signal**: A raw mathematical anomaly (e.g., "Sentence variance is 0.12").
- **Evidence**: A human-readable contextualization (e.g., "The text is highly uniform, commonly associated with generated text").
- **Risk**: A composite 0-100 score weighing the severity of all Evidence.
- **Confidence**: How reliable the Risk score is (e.g., Low confidence if the document is only 40 words long).

We use multiple signals instead of a single detector because a single detector is a black box. If a student is falsely flagged for "low perplexity", we can cross-reference their Writing Fingerprint. If their fingerprint matches the current document, we can lower the risk score, reducing false positives.

---

## 12. Writing Fingerprint
- **Baseline Creation**: Takes previous student submissions and averages their linguistic metrics.
- **Comparison**: Measures standard deviations of the new document against the baseline.
- **Deviation**: If a student historically writes short, fragmented sentences with simple vocabulary, and suddenly submits a heavily complex, uniform essay, a Fingerprint Deviation evidence item is generated.
- **Limitations**: Requires historical data. A student's very first assignment cannot have a fingerprint deviation.

---

## 13. Source Similarity
- **Vectors**: Transforms text into 768-dimensional space.
- **Matching**: Calculates the angle (cosine) between the student's text and a provided source text.
- **Limitations**: This is an investigative tool for a provided source. It is NOT a full Turnitin replacement, as we do not have a 20-billion-page internet archive to scan against. The instructor must provide the suspected reference source.

---

## 14. Paraphrase Analysis
- **Semantic Similarity**: "The quick brown fox" vs "The fast auburn canine" (High).
- **Lexical Similarity**: Exact word overlap (Low).
- **Transformation Indicators**: High semantic + Low Lexical = Highly likely to be a spun/paraphrased text.
- **Limitations**: Extremely skilled human writers can also paraphrase well. This is a flag, not proof of an AI spinning tool.

---

## 15. Evidence Engine
The Evidence Engine solves the "black box" problem. 
**Input Signals -> Evidence Items -> Weighted Risk Calculation -> Instructor Review**

We do NOT simply average everything. If we did, a document that is 100% plagiarized but 0% AI-generated would average out to a 50% "suspicious" score, which is confusing.
Instead, weights are independent. A massive source similarity match immediately spikes the Risk Score to HIGH, even if the AI Linguistic signals are zero.

---

## 16. Risk and Confidence Model
- **Risk Score**: 0-100.
- **Risk Levels**: LOW (0-39), MEDIUM (40-69), HIGH (70-100).
- **Confidence**: LOW (short text, conflicting signals), HIGH (long text, multiple overlapping signals).
- **Outcome Example**: A 200-word text might have a High Risk Score (85) due to uniformity, but a LOW Confidence because 200 words isn't enough statistical data to be certain.

---

## 17. Gemini's Role
**Gemini is NOT the sole AI detector.**
Gemini is strictly used as an **Explanation Layer** and an **Embedding Generator**.
- **What it receives**: The structured JSON array of Evidence Items produced by our deterministic engine.
- **What it produces**: A neutral, non-accusatory summary (e.g., *"The submission shows several signals associated with AI-assisted writing"*).
- **Fallback Behavior**: If Gemini times out, the backend gracefully catches the error and returns a pre-written static fallback summary to ensure the app never crashes.

---

## 18. Database Design

```text
[users] 1────* [students]
                  │
                  *
           [submissions]
             │   │   │
             │   │   └──── 1 [reports] (Gemini Explanation)
             │   │
             │   └──── * [evidence] (Individual flags)
             │
             └──── 1 [analysis_results] (Raw JSON metrics)
```
- `users`: Instructors.
- `students`: Enrolled students, mapped to `users` via RLS.
- `submissions`: Core entity for an uploaded document.
- `analysis_results`: Stores the ML pipeline fingerprint/heuristics as `JSONB`.

---

## 19. Security
- **RLS**: Row Level Security ensures an instructor can only query their own students' data.
- **API File Validation**: FastAPI strictly blocks files >10MB and enforces strict MIME types (txt, pdf, docx).
- **Token Limits**: `orchestrator/service.py` truncates extractions at 25,000 words.
- **Secret Protection**: `SUPABASE_KEY` and `GEMINI_API_KEY` are purely server-side.
- **IDOR Protection**: FastAPI manually cross-references the `student_id` in the upload form against the Supabase `users` table to ensure the logged-in instructor actually owns that student.

---

## 20. Testing
- **Suite**: 51 Pytest tests covering ML modules, Database Repo, API routers, Auth logic.
- **Current Status**: **51/51 Passing** (100% green).
- **Evaluation**: `tests/evaluation` includes a benchmarking script that tracks False Positive Rates specifically on human texts to ensure fairness.

---

## 21. Evaluation Methodology
To ensure ethical ML practices, our framework evaluates:
1. **Human-written data** (Target: 0% False Positives)
2. **AI-generated data** (Target: High Recall)
3. **AI-paraphrased data**
We focus heavily on the **False Positive Rate (FPR)**. It is better to let 10 AI essays slip through than to falsely accuse 1 honest student. 
*(Note: Our current `demo_dataset.json` is for presentation purposes and UI validation, not a scientific benchmark scale).*

---

## 22. Limitations
- AI detection is inherently probabilistic.
- False positives can and will occur.
- Short texts (<50 words) lack statistical weight, causing low confidence.
- Writing fingerprints require a baseline of past assignments to function.
- Source similarity requires the instructor to actively provide the suspected reference material.
- Gemini explanations occasionally suffer from minor hallucination framing if the prompt is altered.

---

## 23. Why This Project Is Different
| Generic AI Detector | PROOFly Investigation System |
|---------------------|------------------------------|
| Outputs a single %  | Outputs categorized Evidence |
| Black-box           | Transparent Heuristics       |
| Ignores student history | Generates a unique Fingerprint |
| Says "Student Cheated" | Says "Instructor Review Recommended" |

---

## 24. Demo Flow
1. **Login**: Go to `/login` and sign in (or show the slick UI slogan). 
2. **Dashboard**: Show the High/Medium/Low risk distribution charts. *(Say: "This is the birds-eye view for an instructor.")*
3. **Upload**: Go to Submissions, upload `demo-ai-1.pdf`. *(Say: "Let's run a suspicious document through our ML pipeline.")*
4. **Processing**: Show the loading state. *(Say: "It's extracting text, building semantic embeddings, and generating heuristics.")*
5. **Investigation Report**: Open the result. *(Say: "Notice we don't just say 90% AI. We show EXACTLY why: low variance, specific transition markers, and an explainable Gemini summary.")*
6. **Highlighting**: Click an Evidence Card. *(Say: "It immediately highlights the offending text, providing actionable proof for a student conversation.")*

---

## 25. Judge Questions and Answers

**Q: How do you detect AI?**
A: We don't use a single "detector." We use a deterministic Evidence Engine that combines statistical variance (like sentence uniformity), lexical diversity, and semantic embeddings to build a risk profile.

**Q: How do you reduce false positives?**
A: By introducing a "Confidence" metric and the "Writing Fingerprint". If a student naturally writes with robotic uniformity, their historical baseline will reflect that, lowering their deviation risk on future papers.

**Q: Why not use an LLM as the detector?**
A: LLMs are terrible at detecting themselves and hallucinate false positives. We use deterministic math for the detection, and use the LLM solely to summarize the math.

*(22 more similarly concise answers included in HACKATHON_QUICK_REFERENCE.md)*

---

## 26. Technical Explanation for Team Members
**Evidence Engine**:
- *What it does*: Adds up scores based on rules.
- *Why we need it*: To turn raw math into something a teacher can read.
- *Simple example*: If a text matches a source exactly, add 50 points to the risk score.

**Embeddings**:
- *What it does*: Turns sentences into arrays of 768 numbers.
- *Why we need it*: To see if two sentences *mean* the same thing, even if different words are used.

---

## 27. Presentation/Pitch Material
**30-second pitch:**
"AI detectors are broken. They give teachers unexplainable percentages, leading to false accusations and ruined trust. PROOFly is an investigative platform that replaces black-box detection with transparent, verifiable evidence, empowering educators to have constructive conversations with their students rather than baseless interrogations."

---

## 28. Future Scope
**Realistic**: 
- Canvas/Blackboard LTI Integration.
- Bulk uploading zip files of 100 submissions.
**Advanced**: 
- Keystroke dynamics mapping (if integrated into an LMS text editor).
- Large-scale internet web-scraping for global source similarity (replacing Turnitin).

---

## 29. Deployment
**Local Setup**:
1. `export GEMINI_API_KEY="..."`, `SUPABASE_URL`, `SUPABASE_KEY`.
2. Python: `pip install -r requirements.txt`, `uvicorn backend.main:app`.
3. Node: `npm install`, `npm run dev`.

**Production**:
- Frontend: Vercel.
- Backend: Docker on Render/Cloud Run. (Uses `uvicorn` on `0.0.0.0:8000`).
- DB: Supabase Cloud.

---

## 30. Project Folder Structure
- `/backend`: FastAPI application, routers, services, Supabase logic.
- `/frontend`: Next.js App Router, Tailwind, Shadcn components.
- `/ml`: The core intelligence layer (Features, Fingerprint, Embeddings, Evidence Engine).
- `/scripts`: The Hackathon demonstration seeder dataset and python scripts.
- `/tests`: Pytest integration suite (51 tests).

---

## 31. API Reference
- `POST /api/analysis/run`: The core ML orchestrator. Requires `file` and `student_id`. Returns `OrchestratorResult`.
- `POST /api/documents/upload`: Simple extraction health endpoint.
- `GET /api/health`: Cloud health-check endpoint.

---

## 32. Final Project Summary
PROOFly successfully shifts the paradigm of academic integrity from **detection** to **investigation**. By architecting a robust FastAPI Python ML pipeline and connecting it to a scalable, RLS-secured Next.js frontend, we've delivered a tool that treats students ethically and empowers instructors with tangible data. 

**Current Implementation Status**: MVP Complete, fully secured, entirely functional. Ready for hackathon presentation.
