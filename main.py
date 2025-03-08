from fastapi import FastAPI, HTTPException
from services.schema import OutlineGeneratorRequest, OutlineGeneratorResponse
from services.utils import load_text_file
from langchain_core.prompts import PromptTemplate  # Fixed import
from langchain_openai import ChatOpenAI  # Changed to ChatOpenAI
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.output_parsers import JsonOutputParser
import os

load_dotenv()

print("Current directory:", os.getcwd())
print("Environment variables:", os.environ)
print("API Key exists?", "OPENAI_API_KEY" in os.environ)

app = FastAPI()
origins = [
    "http://localhost:3000",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the correct model for chat
model = ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"),
                   model="gpt-3.5-turbo",
                   temperature=0.7)  # Changed to ChatOpenAI


@app.get("/")
def root():
    return {"message": "Creating My Teaching Assistant"}


@app.post("/generate-outline", response_model=OutlineGeneratorResponse)
async def generate_outline(request: OutlineGeneratorRequest):
    try:
        # Load template
        template = load_text_file("prompts/outline_generation_prompt.txt")

        # Create prompt template correctly
        prompt = PromptTemplate(
            template=template,
            input_variables=["context", "numberOfSlides", "gradeLevel"]
        )

        # Create chain
        parser = JsonOutputParser(pydantic_object=OutlineGeneratorResponse)
        chain = prompt | model | parser

        # Invoke the chain
        result = await chain.ainvoke({
            "context": request.context,
            "numberOfSlides": request.numberOfSlides,
            "gradeLevel": request.gradeLevel
        })
        
        # Ensure we're returning a properly formatted response
        if isinstance(result, dict) and "outlines" in result:
            return result
        else:
            # If result is not properly formatted, create a valid response
            return OutlineGeneratorResponse(outlines=result if isinstance(result, list) else [str(result)])

    except Exception as e:
        print(f"Error generating outline: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate outline: {str(e)}"
        )
