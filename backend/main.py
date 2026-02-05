from fastapi import FastAPI,HTTPException,Header
from src.data import FakeHospitalDB
from pydantic import BaseModel
from config import API_KEY

app = FastAPI()

class   QueryPayload(BaseModel):
    user_id:str
    query:str
    
@app.get("/health")
def health():
    return {"status":"ok"}

def verify_key(x_api_key: str | None):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")
  
@app.post("/query")
def query(payload: QueryPayload, x_api_key: str | None = Header(default=None)):
    verify_key(x_api_key)

    return {
        "message": "Pipeline not wired yet",
        "input": payload.model_dump()
    }