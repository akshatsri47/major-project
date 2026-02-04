from llm import get_model
from langchain.tools import tool
model = get_model()

@tool
def book_appointment(query:str)-> str:
    """to book an appointment"""
       
    
    