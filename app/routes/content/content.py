from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Query, Form
from app.db.database import db
from app.models import Content, SummaryResponse

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from app.services.generation.generate import GenerationService

import tempfile
import shutil
import os  # For file cleanup
from PyPDF2 import PdfReader

# from nltk.tokenize import sent_tokenize, word_tokenize
# from nltk.corpus import stopwords
# from collections import Counter
# import random
# import nltk

# Ensure nltk dependencies are downloaded
# nltk.download("punkt")
# nltk.download("stopwords")

content_router = APIRouter(prefix="/content", tags=["Content"])

async def get_content(content_id : str):
    contentRes = await db.contents.find_one({"id": content_id})
    if contentRes:
        return Content(**contentRes)
    return None

oauth2service = OAuth2PasswordBearer(tokenUrl="token")


@content_router.post('/create')
async def create_content(content : Content):
    #check if content already exists
    #if exists, return HTTPException
    #else, create content
    if await get_content(content.id):
        raise HTTPException(status_code=400, detail="Content already exists")
    content_dict = {
        "id": content.id,
        "title": content.title,
        "description": content.description,
        "associated_with": content.associated_with.model_dump()
    }
    await db.contents.insert_one(content_dict)
    return {"message": "Content created successfully"}


@content_router.post("/generate_summary", response_model=SummaryResponse)
async def generate_summary(pdf_file: UploadFile):
    try:
        # Save the uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            shutil.copyfileobj(pdf_file.file, temp_file)
            temp_file_path = temp_file.name

        # Initialize the GenerationService with the temporary file path
        generation_service = GenerationService(file_path=temp_file_path)

        # Generate summary
        summary = await generation_service.getSummary(
            {"question" : "Generate a detailed summary of the given document in 300 words."}
        )

        # Generate key concepts
        raw_key_concepts = await generation_service.getKeyConcepts({
           "question" : "Generate me the key points of the document and a short description for each key point. Give me response in the following format: Name of Key Point 1: Description 1\n\n Name of Key Point 2: Description 2\n\n Name of Key Point 3: Description 3 etc. Don't give me any other text or extra strings. Just give me the response in the format I asked. Always generate atleast 3 key points each with a name and description."}
           )
        print(raw_key_concepts)
        key_concepts = [
            {"key_concept": concept["key_point"], "description": concept["description"]}
            for concept in raw_key_concepts
        ]  # Include both key_concept and description

        # Use key concepts as topics (for simplicity)
        topics = [concept["key_concept"] for concept in key_concepts]

        # Generate quizzes (mocked for now, as GenerationService doesn't handle quizzes directly)
        quizzes = [
            {
                "question": f"What is the meaning of '{concept['key_concept']}'?",
                "options": [concept["key_concept"], "Option 2", "Option 3", "Option 4"]
            }
            for concept in key_concepts
        ]

        # Format the response
        formatted_response = {
            "summary": summary.strip(),
            "key_concepts": raw_key_concepts,
            "topics": topics,
            "quizzes": quizzes,
        }

        return formatted_response
    except Exception as e:
        # Log the error for debugging
        print(f"Error processing file: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
    finally:
        # Clean up the temporary file
        pdf_file.file.close()
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)


@content_router.post("/get_key_concept_details")
async def get_key_concept_details(
    pdf_file: UploadFile = File(..., description="The uploaded PDF file"),
    concept: str = Form(..., description="The key concept to extract details for")
):
    try:
        # Save the uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            shutil.copyfileobj(pdf_file.file, temp_file)
            temp_file_path = temp_file.name

        # Initialize the GenerationService with the temporary file path
        generation_service = GenerationService(file_path=temp_file_path)

        # Use the getKeyConceptDetails method to generate detailed information about the key concept
        detailed_info = await generation_service.getKeyConceptDetails(concept)

        return {"concept": concept, "details": detailed_info}
    except Exception as e:
        # Log the error for debugging
        print(f"Error processing key concept details: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing key concept details: {str(e)}")
    finally:
        # Clean up the temporary file
        pdf_file.file.close()
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)


@content_router.post("/generate_quizzes")
async def generate_quizzes(
    pdf_file: UploadFile = File(..., description="The uploaded PDF file"),
    concept: str = Form(..., description="The key concept to generate quizzes for")
):
    try:
        # Save the uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            shutil.copyfileobj(pdf_file.file, temp_file)
            temp_file_path = temp_file.name

        # Initialize the GenerationService with the temporary file path
        generation_service = GenerationService(file_path=temp_file_path)

        # Use the generateQuizzesForKeyConcept method to generate quizzes for the key concept
        quizzes = await generation_service.generateQuizzesForKeyConcept(concept)

        return {"concept": concept, "quizzes": quizzes}
    except Exception as e:
        # Log the error for debugging
        print(f"Error generating quizzes for key concept: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating quizzes for key concept: {str(e)}")
    finally:
        # Clean up the temporary file
        pdf_file.file.close()
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)


@content_router.post("/generate_flashcards")
async def generate_flashcards(
    pdf_file: UploadFile = File(..., description="The uploaded PDF file"),
    concept: str = Form(..., description="The key concept to generate flashcards for")
):
    try:
        # Save the uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            shutil.copyfileobj(pdf_file.file, temp_file)
            temp_file_path = temp_file.name

        # Initialize the GenerationService with the temporary file path
        generation_service = GenerationService(file_path=temp_file_path)

        # Use the generateFlashcardsForKeyConcept method to generate flashcards for the key concept
        flashcards = await generation_service.generateFlashcardsForKeyConcept(concept)

        return {"concept": concept, "flashcards": flashcards}
    except Exception as e:
        # Log the error for debugging
        print(f"Error generating flashcards for key concept: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating flashcards for key concept: {str(e)}")
    finally:
        # Clean up the temporary file
        pdf_file.file.close()
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)