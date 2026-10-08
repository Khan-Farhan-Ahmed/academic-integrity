# Proofly Demo Seeder

This directory contains scripts and sample texts designed to rapidly populate the system with isolated test cases for hackathon and presentation purposes.

## Dataset Structure (`demo_dataset.json`)
Contains 5 distinct academic submission scenarios:
1. **Human-written**: A naturally styled essay about the Industrial Revolution.
2. **AI-generated-style**: A highly uniform, vocabulary-dense response on the same topic.
3. **AI-paraphrased-style**: A rewritten snippet testing the lexical similarity/semantic parity algorithms.
4. **Strong source similarity**: Exact copied phrasing to test vector embedding cosine similarity.
5. **Mixed/ambiguous**: Text containing a blend of robotic transition markers alongside informal human phrasing.

## Seeding the Data

To automatically push these 5 test cases through the real `ml.orchestrator` ML pipeline and insert them into your Supabase database:

1. Ensure your `.env` variables are active:
```bash
export GEMINI_API_KEY="your-gemini-key"
export SUPABASE_URL="your-supabase-url"
export SUPABASE_KEY="your-supabase-service-role-key"
```

2. Run the seeder from the project root:
```bash
python scripts/seed_demo.py
```

### What the script does:
- The script **does not fabricate results**. It takes the raw string texts from `demo_dataset.json` and actively processes them through the `EvidenceEngine`, Gemini explanation layer, and Paraphrase analyzer.
- The resulting JSON outputs are automatically persisted into your connected Supabase `analysis_results` and `evidence` tables.
- **Offline Mode**: If `SUPABASE_KEY` is not detected, the script will gracefully fallback to executing the entire ML pipeline purely in-memory, dumping the pipeline output to `frontend/public/demo_results.json` so you can verify the ML output immediately without configuring a database.
