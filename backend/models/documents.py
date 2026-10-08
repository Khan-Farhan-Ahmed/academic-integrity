from pydantic import BaseModel

class DocumentExtractionResponse(BaseModel):
    filename: str
    file_type: str
    character_count: int
    word_count: int
    extracted_text: str
