import os
import shutil
import uuid
from dotenv import load_dotenv
from fastapi import HTTPException, UploadFile
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter  # Fixed import
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
load_dotenv()
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def load_text_file(file_path: str) -> str:
    """
    Reads a text file and returns its content as a string.

    Args:
        file_path (str): The path to the text file.

    Returns:
        str: The contents of the file.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return content
    except FileNotFoundError:
        print(f"Error: The file at {file_path} was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")


def get_file_vectors(file: str) -> str:
    #PDF Loader
    loader = PyPDFLoader(file)
    documents = loader.load()

    #Text Splitter 

    text_spilitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )

    chunks  = text_spilitter.split_documents(documents)

    CHROMA_PATH = "/Users/dhwanil/Desktop/Presentation_Gen/presentation-generator/Backend/static/db/.chroma"
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)
    
    db = Chroma.from_documents(
                               chunks, 
                               OpenAIEmbeddings(), 
                               persist_directory=CHROMA_PATH
                               )

    db.persist()
    # print(f"Database {len(chunks)} created at {CHROMA_PATH}")
async def save_uploaded_file(file: UploadFile) -> str:
    """Save uploaded file to disk and return path"""
    try:
        # Generate unique filename
        file_ext = os.path.splitext(file.filename)[1]
        file_name = f"{uuid.uuid4()}{file_ext}"
        file_path = os.path.join(UPLOAD_DIR, file_name)

        # Save file contents
        contents = await file.read()
        with open(file_path, "wb") as buffer:
            buffer.write(contents)
            
        return file_path
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File save failed: {str(e)}")
    finally:
        await file.close()

# generate_RAG_response()