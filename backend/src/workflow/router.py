from paydantic import BaseModel,Field
from .state import Classification
from llm import get_model

class ClassificationResult(BaseModel):
    """classify the user query into proper sub-agent """
    classifications:list[Classification] = Field(description="SELECT THE APPROPIATE AGENT FOR THE TASK ")
     
def classify_query(state:RouterState) -> dict:
    
