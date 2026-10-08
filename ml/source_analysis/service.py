import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from ml.source_analysis.models import ReferenceDocument, MatchDetail, SourceSimilarityResult
from ml.source_analysis.chunking import chunk_text
from ml.embeddings.service import get_raw_embeddings

def calculate_similarity(submission_text: str, references: list[ReferenceDocument], threshold: float = 0.85) -> SourceSimilarityResult:
    if not submission_text or not submission_text.strip() or not references:
        return SourceSimilarityResult(
            overall_similarity_score=0.0,
            strong_match_percentage=0.0,
            top_matches=[]
        )
        
    sub_chunks = chunk_text(submission_text)
    if not sub_chunks:
        return SourceSimilarityResult(
            overall_similarity_score=0.0,
            strong_match_percentage=0.0,
            top_matches=[]
        )
        
    # Get embeddings for submission
    sub_embeds = get_raw_embeddings(sub_chunks)
    
    # Process references
    all_ref_chunks = []
    ref_embed_map = []  # To map embedding index back to (doc_id, chunk_text)
    
    for ref in references:
        r_chunks = chunk_text(ref.text)
        for rc in r_chunks:
            all_ref_chunks.append(rc)
            ref_embed_map.append((ref.id, rc))
            
    if not all_ref_chunks:
        return SourceSimilarityResult(
            overall_similarity_score=0.0,
            strong_match_percentage=0.0,
            top_matches=[]
        )
        
    ref_embeds = get_raw_embeddings(all_ref_chunks)
    
    # Compute similarity matrix
    sim_matrix = cosine_similarity(sub_embeds, ref_embeds)
    
    matches = []
    strong_match_count = 0
    
    # Analyze each submission chunk against all reference chunks
    for i, sub_chunk in enumerate(sub_chunks):
        best_ref_idx = np.argmax(sim_matrix[i])
        best_score = float(sim_matrix[i][best_ref_idx])
        
        if best_score >= threshold:
            strong_match_count += 1
            ref_id, ref_chunk = ref_embed_map[best_ref_idx]
            matches.append(MatchDetail(
                submission_chunk=sub_chunk,
                reference_id=ref_id,
                reference_chunk=ref_chunk,
                similarity_score=best_score
            ))
            
    # Calculate overall metrics
    strong_match_percentage = (strong_match_count / len(sub_chunks)) * 100.0
    
    # Overall score could be average of best matches, or just the strong match percentage.
    # Let's use the average of the top matched scores if there are matches, else 0.
    if matches:
        overall_similarity_score = sum(m.similarity_score for m in matches) / len(matches) * 100.0
    else:
        overall_similarity_score = 0.0
        
    # Sort top matches by score descending
    matches.sort(key=lambda x: x.similarity_score, reverse=True)
    top_matches = matches[:10]  # Return top 10 strongest matches
    
    return SourceSimilarityResult(
        overall_similarity_score=overall_similarity_score,
        strong_match_percentage=strong_match_percentage,
        top_matches=top_matches
    )
