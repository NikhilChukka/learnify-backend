from pydantic import BaseModel, Field
from typing import List, Dict

class UserIn(BaseModel):
    username: str
    password: str

class User(BaseModel):
    username: str
    hashed_password: str

class UserForContent(BaseModel):
    username: str

class Content(BaseModel):
    id: str
    title: str
    description: str
    associated_with: UserForContent

class ContentIn(BaseModel):
    id: str

class KeyConcept(BaseModel):
    key_concept: str
    description: str

class SummaryResponse(BaseModel):
    summary: str
    key_concepts: List[KeyConcept]  # Use the KeyConcept model for better validation
    topics: List[str]  # Topics can remain as a list of strings
    quizzes: List[dict]

    class Config:
        json_schema_extra = {
            "example": {
                "summary": "This is a brief summary of the document.",
                "key_concepts": [
                    {"key_concept": "Term-document Matrix", "description": "A matrix representing documents as vectors of term frequencies."},
                    {"key_concept": "TF-IDF", "description": "A statistical measure used to evaluate the importance of a term in a document."}
                ],
                "topics": ["Term-document Matrix", "TF-IDF"],
                "quizzes": [
                    {
                        "question": "What is the main idea of the term-document matrix?",
                        "options": ["Option 1", "Option 2", "Option 3", "Option 4"]
                    }
                ]
            }
        }