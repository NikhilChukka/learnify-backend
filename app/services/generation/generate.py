import os
import getpass
import asyncio
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain.chat_models import init_chat_model
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain import hub
from dotenv import load_dotenv
from langgraph.graph import START, StateGraph
from typing_extensions import List, TypedDict
from langchain_core.documents import Document

load_dotenv()

os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGSMITH_API_KEY"] = os.getenv("LANGSMITH_API_KEY")

class GenerationService:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
        self.llm = init_chat_model("llama3-8b-8192", model_provider="groq")
        self.vector_store = InMemoryVectorStore(embedding=self.embeddings)
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200, add_start_index=True)
        self.prompt = hub.pull("rlm/rag-prompt")
    
    async def get_pdf_text(self) -> List[Document]:
        loader = PyPDFLoader(self.file_path)
        pages = []
        async for page in loader.alazy_load():
            pages.append(page)
        return pages

    async def process(self) -> StateGraph:
        # Extract text from the PDF
        pages = await self.get_pdf_text()
        # Use text splitter to create chunks
        all_splits = self.text_splitter.split_documents(pages)
        self.vector_store.add_documents(documents=all_splits)
        
        # Build the retrieval and generation pipeline graph
        class State(TypedDict):
            question: str
            context: List[Document]
            answer: str
        
        def retrieve(state: State):
            retieved_docs = self.vector_store.similarity_search(state["question"])
            state["context"] = retieved_docs
            return state

        def generate(state: State):
            docs_content = '\n\n'.join([doc.page_content for doc in state["context"]])
            messages = {"question": state["question"], "context": docs_content}  # Ensure messages is a dict
            response = self.llm.invoke(messages)
            state["answer"] = response.content.strip()  # Ensure the response is properly extracted
            return state  # Return the updated state as a dict

        graph_builder = StateGraph(State).add_sequence([retrieve, generate])
        graph_builder.add_edge(START, "retrieve")
        graph = graph_builder.compile()
        return graph
    
    async def getSummary(self, question: dict) -> dict:
        graph = await self.process()
        result = graph.invoke(question)
        return result["answer"]  # Ensure the correct key is accessed
    
    async def getKeyConcepts(self, question1: dict) -> dict:
        graph = await self.process()
        question1 = {"question" : "Generate me the key points of the document and a short description for each key point. Give me response in the following format: Name of Key Point 1: Description 1\n\n Name of Key Point 2: Description 2\n\n Name of Key Point 3: Description 3 etc. Don't give me any other text or extra strings. Just give me the response in the format I asked. Always generate atleast 3 key points each with a name and description."}         
        result = graph.invoke(question1)
        output = result["answer"].strip().split("\n\n")[1].split("\n")
        key_concepts = [{"key_point": item.split(":")[0].strip(), "description": item.split(":")[1].strip()} for item in output if ":" in item]
        
        return key_concepts
    
    async def getKeyConceptDetails(self, concept: str) -> str:
        """
        Generate detailed information about a specific key concept.
        """
        graph = await self.process()
        question = {"question": f"Provide detailed information about the key concept: {concept}"}
        result = graph.invoke(question)
        detailed_info = result['answer'].content.strip()
        return detailed_info

    async def generateQuizzesForKeyConcept(self, concept: str) -> List[dict]:
        """
        Generate quizzes (questions and answers) for a specific key concept.
        """
        graph = await self.process()
        question = {"question": f"Generate 3 quiz questions and answers for the key concept: {concept}"}
        result = graph.invoke(question)
        quizzes_raw = result['answer'].content.strip().split("\n\n")
        quizzes = []
        for quiz in quizzes_raw:
            if ":" in quiz:
                question, answer = quiz.split(":", 1)
                quizzes.append({"question": question.strip(), "answer": answer.strip()})
        return quizzes

    async def generateFlashcardsForKeyConcept(self, concept: str) -> List[dict]:
        """
        Generate flashcards (question-answer pairs) for a specific key concept.
        """
        graph = await self.process()
        question = {"question": f"Generate 10 flashcards (question-answer pairs) for the key concept: {concept}"}
        result = graph.invoke(question)
        flashcards_raw = result['answer'].content.strip().split("\n\n")
        flashcards = []
        for flashcard in flashcards_raw:
            if ":" in flashcard:
                question, answer = flashcard.split(":", 1)
                flashcards.append({"question": question.strip(), "answer": answer.strip()})
        return flashcards


if __name__ == "__main__":
    service = GenerationService(file_path="/Users/nikhilchukka/Desktop/learnify/learnify2/backend-fastapi/fabula.pdf")
    
    question1 = {"question": "Extract key points from the document with a short description for each. Format the response strictly as follows:\n\nKey Point 1: Description 1\nKey Point 2: Description 2\nKey Point 3: Description 3\n\nDo not include any additional text, extra strings, or deviations from this format. Ensure the response adheres exactly to the specified structure."}
        
    resultsKeyConcepts = asyncio.run(service.getKeyConcepts(question1))

    output = resultsKeyConcepts['answer'].content.strip().split("\n\n")[1].split("\n")
    key_concepts = [{"key_point": item.split(":")[0].strip(), "description": item.split(":")[1].strip()} for item in output if ":" in item]
    print("output ",  output, "\nKey Concepts List:\n", key_concepts, "\n\n")


    # # Example usage for key concept details
    # resultDetails = asyncio.run(service.getKeyConceptDetails("Artificial Intelligence"))
    # print(resultDetails)
    # # Example usage for quizzes
    # resultQuizzes = asyncio.run(service.generateQuizzesForKeyConcept("Artificial Intelligence"))
    # print(resultQuizzes)
    # # Example usage for flashcards
    # resultFlashcards = asyncio.run(service.generateFlashcardsForKeyConcept("Artificial Intelligence"))
    # print(resultFlashcards)
    # resultSummary = asyncio.run(service.getSummary(
    # question = {"question" : "generate me the summary of the document in 300 words."}
    # ))
    # print(resultSummary)

