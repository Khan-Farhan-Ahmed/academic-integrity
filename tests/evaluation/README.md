# Proofly Evaluation & Benchmarking Framework

This directory contains the reproducible evaluation framework for the Proofly Academic Integrity System. It tests the isolated and combined performance of the AI Linguistic Signal engine and the Evidence Engine.

## Structure
- `dataset.json`: The benchmark dataset containing ground truth labels.
- `evaluate.py`: The evaluation script that processes the dataset through the ML pipeline.

## Methodology
The evaluation script (`evaluate.py`) tests the system on binary classification mapping:
- **Positive Class (AI)**: `ai-generated`, `ai-paraphrased`, `mixed`
- **Negative Class (Human)**: `human`

The system classifies a submission as "Predicted AI" if the Evidence Engine assigns a `HIGH` or `MEDIUM` risk level. A `LOW` risk level maps to "Predicted Human".

### Evaluated Modules
- Feature Extraction (`ml.features`)
- AI Linguistic Heuristics (`ml.ai_detection`)
- Evidence Engine Risk Scoring (`ml.evidence_engine`)

*Note: Fingerprinting and source similarity require external database baselines and are bypassed in this specific pure-linguistic offline benchmark to isolate text-level heuristic accuracy.*

## Metrics Explained
- **Accuracy**: Overall correct classifications.
- **Precision**: Accuracy of AI flags (how often an AI flag is actually AI).
- **Recall**: Detection rate of actual AI content.
- **F1 Score**: Harmonic mean of Precision and Recall.
- **False Positive Rate (FPR)**: **Critical Metric.** The percentage of entirely human-written texts falsely flagged as HIGH/MEDIUM risk. The system is tuned to minimize this metric.
- **False Negative Rate (FNR)**: The percentage of AI texts that successfully bypass detection.

## Current Limitations
**INSUFFICIENT REAL DATA:** The current `dataset.json` is a toy benchmark dataset containing only 4 synthetic examples to demonstrate the execution of the evaluation framework. 

**DO NOT USE THESE RESULTS TO CLAIM REAL-WORLD ACCURACY.** A statistically significant dataset (10,000+ texts) with verified genuine human baselines and varied LLM generation parameters (temperature, models) is required to establish production-grade benchmarks.

## Running the Framework
Execute the evaluation script from the project root:
```bash
python -m tests.evaluation.evaluate
```
