import json
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from ml.features.extractor import extract_features
from ml.ai_detection.engine import analyze_signals
from ml.evidence_engine.service import calculate_evidence
from ml.evidence_engine.models import EvidenceEngineRequest

def load_dataset():
    dataset_path = os.path.join(os.path.dirname(__file__), 'dataset.json')
    with open(dataset_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def run_evaluation():
    print("="*60)
    print("  PROOFly - Academic Integrity System Evaluation Framework")
    print("="*60)
    
    dataset = load_dataset()
    print(f"Loaded {len(dataset)} samples from dataset.")
    print("WARNING: This is a toy benchmark dataset for framework demonstration.")
    print("Results DO NOT represent real-world accuracy.\n")
    
    metrics = {
        "TP": 0, "FP": 0, "TN": 0, "FN": 0
    }
    
    results = []

    for item in dataset:
        text = item["text"]
        label = item["label"]
        
        is_ground_truth_ai = label in ["ai-generated", "ai-paraphrased", "mixed"]
        
        # Run ML Pipeline
        features = extract_features(text)
        ai_signals = analyze_signals(text)
        
        req = EvidenceEngineRequest(
            word_count=len(text.split()),
            ai_signals=ai_signals,
            fingerprint_comparison=None,
            source_similarity=None,
            paraphrase_analysis=None
        )
        
        engine_res = calculate_evidence(req)
        
        # Classification thresholds
        # For our system, HIGH or MEDIUM risk is a positive AI flag requiring review.
        # LOW is negative (human).
        predicted_ai = engine_res.risk_level in ["HIGH", "MEDIUM"]
        
        if is_ground_truth_ai and predicted_ai:
            metrics["TP"] += 1
            res = "True Positive"
        elif not is_ground_truth_ai and predicted_ai:
            metrics["FP"] += 1
            res = "FALSE POSITIVE"
        elif not is_ground_truth_ai and not predicted_ai:
            metrics["TN"] += 1
            res = "True Negative"
        elif is_ground_truth_ai and not predicted_ai:
            metrics["FN"] += 1
            res = "FALSE NEGATIVE"
            
        results.append({
            "id": item["id"],
            "label": label,
            "risk_level": engine_res.risk_level,
            "score": engine_res.overall_risk_score,
            "result": res
        })

    # Calculate aggregate metrics
    TP = metrics["TP"]
    FP = metrics["FP"]
    TN = metrics["TN"]
    FN = metrics["FN"]
    
    total = TP + FP + TN + FN
    accuracy = (TP + TN) / total if total > 0 else 0
    precision = TP / (TP + FP) if (TP + FP) > 0 else 0
    recall = TP / (TP + FN) if (TP + FN) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    fpr = FP / (FP + TN) if (FP + TN) > 0 else 0
    fnr = FN / (FN + TP) if (FN + TP) > 0 else 0

    print("--- Detailed Results ---")
    for r in results:
        print(f"[{r['id']}] Truth: {r['label'].ljust(15)} | Predicted Risk: {r['risk_level'].ljust(6)} (Score: {r['score']:.1f}) -> {r['result']}")
        
    print("\n--- Confusion Matrix ---")
    print(f"                 Predicted AI    Predicted Human")
    print(f"Actual AI        {str(TP).ljust(15)} {str(FN).ljust(15)}")
    print(f"Actual Human     {str(FP).ljust(15)} {str(TN).ljust(15)}")
    
    print("\n--- Performance Metrics ---")
    print(f"Accuracy:              {accuracy:.2f}")
    print(f"Precision:             {precision:.2f}")
    print(f"Recall (Sensitivity):  {recall:.2f}")
    print(f"F1 Score:              {f1:.2f}")
    print(f"False Positive Rate:   {fpr:.2f}  <-- CRITICAL METRIC (Rate of falsely accusing human-written text)")
    print(f"False Negative Rate:   {fnr:.2f}")
    print("\n============================================================")
    print("EVALUATION COMPLETED.")

if __name__ == "__main__":
    run_evaluation()
