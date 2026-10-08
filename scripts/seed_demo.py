import os
import sys
import json
import uuid

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ml.orchestrator.service import run_orchestrator

def main():
    print("=========================================")
    print("  PROOFly - Hackathon Demo Seed Script   ")
    print("=========================================")
    
    if not os.environ.get("GEMINI_API_KEY"):
        print("\n[WARNING] GEMINI_API_KEY is not set in the environment.")
        print("The ML pipeline will run, but the 'Explanation' phase will use generic fallback text.")
        print("To generate real LLM summaries, export GEMINI_API_KEY before running this script.\n")
        
    if not os.environ.get("SUPABASE_KEY"):
        print("\n[WARNING] SUPABASE_KEY is not set.")
        print("The ML pipeline will run perfectly in-memory and write a JSON dump, but data will NOT be inserted into Supabase DB.\n")
    
    dataset_path = os.path.join(os.path.dirname(__file__), 'demo_dataset.json')
    with open(dataset_path, 'r', encoding='utf-8') as f:
        dataset = json.load(f)
        
    results_list = []
    
    for case in dataset:
        print(f"\nProcessing Case: {case['case']}")
        print(f"Student ID: {case['student_id']}")
        
        # We process the text by encoding it to bytes for the orchestrator
        file_bytes = case['text'].encode('utf-8')
        
        try:
            # We bypass Fastapi API and hit the orchestrator directly.
            # This ensures the REAL ML pipeline is run without faking analysis results.
            result = run_orchestrator(
                student_id=case['student_id'],
                assignment_name=case['assignment_name'],
                filename=f"{case['id']}.txt",
                file_type="text/plain",
                file_bytes=file_bytes,
                reference_sources=case.get('reference_sources')
            )
            
            # Print highlights
            print(f" -> Risk Score: {result.risk_score}")
            print(f" -> Risk Level: {result.risk_level}")
            if result.gemini_explanation:
                print(f" -> Summary: {result.gemini_explanation.executive_summary[:100]}...")
                
            results_list.append(result.model_dump())
            
        except Exception as e:
            print(f" -> FAILED to process case: {str(e)}")

    # Save to a local JSON file that the frontend can read if the DB is offline
    output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend', 'public', 'demo_results.json'))
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results_list, f, indent=2)
        
    print("\n=========================================")
    print(f"Seed process complete. {len(results_list)} cases processed.")
    print(f"Local fallback demo data saved to: {output_path}")
    print("If Supabase was running locally, these records are now inserted into the database.")
    print("=========================================")

if __name__ == "__main__":
    main()
