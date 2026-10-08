import re

def chunk_text(text: str, chunk_size_words: int = 50, overlap_words: int = 15) -> list[str]:
    """Splits text into sliding windows of words."""
    if not text or not text.strip():
        return []
        
    words = re.findall(r'\S+', text)
    if not words:
        return []
        
    chunks = []
    i = 0
    while i < len(words):
        chunk_words = words[i:i + chunk_size_words]
        chunks.append(" ".join(chunk_words))
        i += (chunk_size_words - overlap_words)
        
        # Avoid infinite loops or tiny final chunks if we just stepped forward but not enough
        if i >= len(words):
            break
            
    return chunks
