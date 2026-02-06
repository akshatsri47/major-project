from fastapi import FastAPI,HTTPException,Header
from src.data import FakeHospitalDB
from pydantic import BaseModel,EmailStr
from datetime import date,time
from config import API_KEY,MONGODBURI,MONGODB_DB_NAME,collection_name,collection_name2
from pymongo import AsyncMongoClient
from uuid import uuid4


app = FastAPI()

client = AsyncMongoClient(MONGODBURI)
db = client[MONGODB_DB_NAME]
appointment_collection = db[collection_name2]
medical_colllection = db[collection_name]
class   QueryPayload(BaseModel):
    user_id:str
    query:str
class available_slot(BaseModel):
    date:date
    times:list[time]

class Doctormodel(BaseModel):
    name:str
    available_slots:list[available_slot]
    email:EmailStr
    specialty:str

class Doctorcollection(BaseModel):
    doctors:list[Doctormodel]

class Appointmentmodel(BaseModel):
    appointment_id : str = str(uuid4())
    doctor_email:EmailStr
    patient_name:str
    patient_email:EmailStr
    patient_id:str
    date:date
    time:time
    status: str = "booked"

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
#doctor endpoints
@app.get("/getdoc")
async def getdoctor():
    docs =  await medical_colllection.find().to_list()
    return Doctorcollection(
        doctors = [Doctormodel(**doc) for doc in docs]
    )


@app.get("/getdoc/{specialty}")
async def getdocbyspec(specialty:str):
    cursor = medical_colllection.find(
        {"specialty":specialty}
    )
    docs =  await cursor.to_list(100)
    return  Doctorcollection(
        doctors = [Doctormodel(**doc) for doc in docs]
    )

@app.post("/book")
async def book_appointment(payload: Appointmentmodel):

    # find doctor
    doctor = await medical_colllection.find_one(
        {"email": payload.doctor_email}
    )

    if not doctor:
        raise HTTPException(404, "Doctor not found")

    slot_found = False
    time_str = payload.time.isoformat(timespec="minutes")

    # check availability
    for slot in doctor["available_slots"]:
        if slot["date"] == payload.date.isoformat():

            if time_str in slot["times"]:
                slot["times"].remove(time_str)
                slot_found = True
                break

    if not slot_found:
        raise HTTPException(400, "Slot unavailable")

    # update doctor availability
    await medical_colllection.update_one(
        {"email": payload.doctor_email},
        {"$set": {"available_slots": doctor["available_slots"]}},
    )

    # insert appointment record
    await appointment_collection.insert_one(
        payload.model_dump()
    )

    return {
        "status": "confirmed",
        "appointment_id": payload.appointment_id,
        "doctor": payload.doctor_email,
        "patient": payload.patient_name,
        "date": payload.date,
        "time": payload.time,
    }


@app.get("/appointment/{appointment_id}")
async def get_appointment(appointment_id: str):

    appt = await appointments_collection.find_one(
        {"appointment_id": appointment_id}
    )

    if not appt:
        raise HTTPException(404, "Not found")

    return appt
