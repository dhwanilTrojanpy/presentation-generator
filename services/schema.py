from enum import Enum
from pydantic import BaseModel, Field

class GradeLevel(str, Enum):
    HIGHSCHOOL = "HIGHSCHOOL"
    COLLEGE = "COLLEGE"
    PHD = "PHD"
 
class OutlineGeneratorRequest(BaseModel):
    context : str = Field(..., description="The prompt to generate the outline for")
    numberOfSlides : int = Field(default=5,description="The number of slides to generate")
    gradeLevel : GradeLevel = Field(default="HIGHSCHOOL",description="The grade level of the outline")

class OutlineGeneratorResponse(BaseModel):
    outlines : list[str] = Field(..., description="The generated outline")

