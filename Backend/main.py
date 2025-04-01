from fastapi import FastAPI, HTTPException, UploadFile, Form
from services.schema import OutlineGeneratorRequest, OutlineGeneratorResponse, PresentationRequest, SlideContentRequest
from services.utils import clean_markup_content, save_uploaded_file, load_text_file, get_file_vectors
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import GoogleGenerativeAI
from fastapi.middleware.cors import CORSMiddleware
import os
from pydantic import BaseModel
from dotenv import load_dotenv
import vertexai
from vertexai.preview.vision_models import ImageGenerationModel

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
vertexai.init(project=project_id, location=location)

# Initialize the model for chat
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
            db = await get_file_vectors(file_path)

        template = load_text_file("prompts/outline_generation_prompt.txt")
        prompt = PromptTemplate(
            template=template,
            input_variables=["context", "numberOfSlides", "gradeLevel"])

        chain = prompt | model
        raw_result = await chain.ainvoke({
            "context": context,
            "numberOfSlides": numberOfSlides,
            "gradeLevel": gradeLevel
        })

        content = raw_result.content if hasattr(raw_result, 'content') else str(raw_result)
        outlines = []
        for line in content.split('\n'):
            line = line.strip()
            if line and (line.startswith('**') or line.startswith('1.') or line[0].isdigit() and '.' in line[:5]):
                clean_line = line.replace('**', '').strip().replace('"', '')
                outlines.append(clean_line)

        return OutlineGeneratorResponse(outlines=outlines)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate outline: {str(e)}")

@app.post("/generate-slide-content", response_model=dict)
async def generate_slide_content(request: SlideContentRequest):
    try:
        template = load_text_file("prompts/slide_content_generation_prompt.txt")
        template_types = ["titleAndBody", "titleAndBullets", "twoColumn", "sectionHeader"]
        slide_contents = []

        for i, outline in enumerate(request.outlines):
            template_type = template_types[i % len(template_types)]
            if i == len(request.outlines) - 2:
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
            cleaned_content = clean_markup_content(content)
            slide_contents.append(cleaned_content)

        return {"slides": slide_contents}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate presentation: {str(e)}")

@app.post("/generate-presentation")
async def generate_presentation(request: PresentationRequest):
    try:
        image_model = ImageGenerationModel.from_pretrained("imagen-3.0-generate-002")
        image_prompt_template = load_text_file("prompts/slide_image_prompt.txt")
        if not image_prompt_template:
            raise HTTPException(status_code=500, detail="Failed to load image prompt template")

        processed_slides = []

        for slide in request.slides:
            key_points = ""
            if isinstance(slide, dict):
                if slide.get("template") == "titleAndBody":
                    key_points = slide.get("body", "")
                elif slide.get("template") == "titleAndBullets":
                    key_points = "\n".join(slide.get("bullets", []))
                elif slide.get("template") == "twoColumn":
                    key_points = f"{slide.get('leftColumn', {}).get('body', '')}\n{slide.get('rightColumn', {}).get('body', '')}"

                prompt = PromptTemplate(
                    template=image_prompt_template,
                    input_variables=["slide_title", "template_type", "key_points"]
                )

                prompt_result = prompt.format(
                    slide_title=slide.get("title", ""),
                    template_type=slide.get("template", ""),
                    key_points=key_points
                )

            try:
                images = image_model.generate_images(
                    prompt=prompt_result,
                    number_of_images=1,
                )

                if images:
                    image_path = f"static/images/slide_{len(processed_slides)}.jpg"
                    images[0].save(image_path)
                    slide["image_url"] = image_path
            except Exception as img_error:
                print(f"Image generation error: {str(img_error)}")
                slide["image_url"] = None

            processed_slides.append(slide)
        print(processed_slides)    
        return {"message": "Presentation processed successfully", "slides": processed_slides}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process presentation: {str(e)}")