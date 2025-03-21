from fastapi import FastAPI, HTTPException, UploadFile, Form
from services.schema import OutlineGeneratorRequest, OutlineGeneratorResponse
from services.utils import save_uploaded_file, load_text_file, get_file_vectors
from langchain_core.prompts import PromptTemplate  # Fixed import
# from langchain_openai import ChatOpenAI  # Changed to ChatOpenAI
# from langchain_google_vertexai import VertexAI  # Using Vertex AI for chat
# import vertexai
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAI
from fastapi.middleware.cors import CORSMiddleware
# from langchain_core.output_parsers import JsonOutputParser
import os
from pydantic import BaseModel

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

project_id = os.getenv("GCP_PROJECT_ID")
location = os.getenv("GCP_LOCATION")
# vertexai.init(project=project_id, location=location)

# Initialize the correct model for chat
model = GoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.7)



@app.get("/")
def root():
    return {"message": "Creating My Teaching Assistant"}


@app.post("/generate-outline", response_model=OutlineGeneratorResponse)
async def generate_outline(context: str = Form(...),
                           numberOfSlides: int = Form(...),
                           gradeLevel: str = Form(...),
                           file: UploadFile = None):
    try:
        file_path = None
        if file:
            file_path = await save_uploaded_file(file)
            print(f"File saved at {file_path}")
            db = await get_file_vectors(file_path)
            print(f"DB: {db}")
        template = load_text_file("prompts/outline_generation_prompt.txt")

        # Create prompt template correctly
        prompt = PromptTemplate(
            template=template,
            input_variables=["context", "numberOfSlides", "gradeLevel"])

        # Invoke the chain
        chain = prompt | model
        # Invoke the chain to get raw output
        raw_result = await chain.ainvoke({
            "context": context,
            "numberOfSlides": numberOfSlides,
            "gradeLevel": gradeLevel
        })
        # print("raw_result ", raw_result)

        # print("Raw result ---->>>>> ", raw_result)

        # Ensure we're returning a properly formatted response
        if hasattr(raw_result, 'content'):
            content = raw_result.content
        else:
            content = str(raw_result)

        # Parse the list items from the output
        outlines = []
        for line in content.split('\n'):
            line = line.strip()

            # Look for lines that start with a number followed by a period
            if line and (line.startswith('**') or line.startswith('1.')
                         or line[0].isdigit() and '.' in line[:5]):
                # Clean up the outline text
                clean_line = line.replace('**', '').strip().replace('"', '')
                outlines.append(clean_line)

        # Return the properly formatted response
        return OutlineGeneratorResponse(outlines=outlines)

    except Exception as e:
        print(f"Error generating outline: {str(e)}")
        raise HTTPException(status_code=500,
                            detail=f"Failed to generate outline: {str(e)}")


class PresentationRequest(BaseModel):
    outlines: list[str]

@app.post("/generate-presentation")
async def generate_presentation(request: PresentationRequest):
    try:
        template = load_text_file("prompts/slide_content_generation_prompt.txt")
        template_types = ["titleAndBody", "titleAndBullets", "twoColumn", "sectionHeader"]
        slide_contents = []

        for i, outline in enumerate(request.outlines):
            # Select template type based on content and position
            template_type = template_types[i % len(template_types)]
            if i == len(request.outlines) - 2:  # Ensure one twoColumn template
                template_type = "twoColumn"

            prompt = PromptTemplate(
                template=template,
                input_variables=["slide_title", "grade_level", "template_type"]
            )

            chain = prompt | model
            result = await chain.ainvoke({
                "slide_title": outline,
                "grade_level": "UNIVERSITY",
                "template_type": template_type
            })

            content = result.content if hasattr(result, 'content') else str(result)
            slide_contents.append(content)

        return {"slides": slide_contents}

    except Exception as e:
        print(f"Error generating presentation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate presentation: {str(e)}")