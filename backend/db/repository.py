import os
from supabase import create_client, Client
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

def get_supabase_client() -> Optional[Client]:
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    if not url or not key:
        return None
    return create_client(url, key)

class DatabaseRepository:
    def __init__(self):
        self.client = get_supabase_client()
        
    def _is_active(self):
        return self.client is not None

    def save_submission(self, student_id: str, assignment_name: str) -> Optional[dict]:
        if not self._is_active():
            return None
        response = self.client.table("submissions").insert({
            "student_id": student_id,
            "assignment_name": assignment_name,
            "status": "pending"
        }).execute()
        return response.data[0] if response.data else None

    def save_document(self, submission_id: str, filename: str, file_type: str, char_count: int, word_count: int, extracted_text: str) -> Optional[dict]:
        if not self._is_active():
            return None
        response = self.client.table("documents").insert({
            "submission_id": submission_id,
            "filename": filename,
            "file_type": file_type,
            "character_count": char_count,
            "word_count": word_count,
            "extracted_text": extracted_text
        }).execute()
        return response.data[0] if response.data else None

    def save_analysis_results(self, submission_id: str, linguistic: dict = None, ai_signals: dict = None, source_similarity: dict = None, paraphrase: dict = None, fingerprint: dict = None) -> Optional[dict]:
        if not self._is_active():
            return None
        response = self.client.table("analysis_results").insert({
            "submission_id": submission_id,
            "linguistic_features": linguistic,
            "ai_signals": ai_signals,
            "source_similarity": source_similarity,
            "paraphrase_analysis": paraphrase,
            "fingerprint_comparison": fingerprint
        }).execute()
        return response.data[0] if response.data else None

    def save_evidence(self, submission_id: str, evidence_items: List[dict]) -> Optional[List[dict]]:
        if not self._is_active():
            return None
            
        payload = []
        for item in evidence_items:
            payload.append({
                "submission_id": submission_id,
                "category": item["category"],
                "signal_name": item["signal_name"],
                "score": item["score"],
                "severity": item["severity"],
                "description": item["description"],
                "supporting_metrics": item["supporting_metrics"],
                "reliability": item["reliability"],
                "contribution_to_risk": item["contribution_to_risk"]
            })
            
        if not payload:
            return []
            
        response = self.client.table("evidence").insert(payload).execute()
        return response.data
        
    def save_report(self, submission_id: str, overall_risk_score: float, risk_level: str, evidence_strength: str, confidence: str, warnings: List[str], conclusion: str, explanation: dict) -> Optional[dict]:
        if not self._is_active():
            return None
        response = self.client.table("reports").insert({
            "submission_id": submission_id,
            "overall_risk_score": overall_risk_score,
            "risk_level": risk_level,
            "evidence_strength": evidence_strength,
            "confidence": confidence,
            "safeguard_warnings": warnings,
            "engine_conclusion": conclusion,
            "gemini_explanation": explanation
        }).execute()
        
        # Mark submission as completed
        self.client.table("submissions").update({"status": "completed"}).eq("id", submission_id).execute()
        
        return response.data[0] if response.data else None
