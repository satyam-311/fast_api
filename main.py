from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Optional, Literal
import json, os

app = FastAPI(title="Patient API", version="1.0")
DATA_FILE = "patients.json"

# ---------------------------
# Utility functions
# ---------------------------
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ---------------------------
# Models
# ---------------------------
class Patient(BaseModel):
    id: Annotated[str, Field(..., description="ID of the patient", examples=["P001"])]
    name: Annotated[str, Field(..., description="Name of the patient")]
    city: Annotated[str, Field(..., description="City where the patient is living")]
    age: Annotated[int, Field(..., gt=0, lt=120, description="Age of the patient")]
    gender: Annotated[Literal["male", "female", "others"], Field(..., description="Gender of the patient")]
    height: Annotated[float, Field(..., gt=0, description="Height of the patient in meters")]
    weight: Annotated[float, Field(..., gt=0, description="Weight of the patient in kgs")]

    @computed_field
    @property
    def bmi(self) -> float:
        return round(self.weight / (self.height ** 2), 2)

    @computed_field
    @property
    def verdict(self) -> str:
        if self.bmi < 18.5:
            return "Underweight"
        elif self.bmi < 25:
            return "Normal"
        elif self.bmi < 30:
            return "Overweight"
        else:
            return "Obese"

class PatientUpdate(BaseModel):
    name: Annotated[Optional[str], Field(default=None)]
    city: Annotated[Optional[str], Field(default=None)]
    age: Annotated[Optional[int], Field(default=None, gt=0)]
    gender: Annotated[Optional[Literal["male", "female", "others"]], Field(default=None)]
    height: Annotated[Optional[float], Field(default=None, gt=0)]
    weight: Annotated[Optional[float], Field(default=None, gt=0)]

# ---------------------------
# Root
# ---------------------------
@app.get("/")
def root():
    return {"msg": "Welcome to the Patient API 🚑. Use /docs to explore."}

# ---------------------------
# CRUD Endpoints
# ---------------------------

# GET all patients
@app.get("/patients")
def get_all_patients():
    data = load_data()
    return {pid: Patient(**p).model_dump() for pid, p in data.items()}

# GET a single patient
@app.get("/patients/{pid}")
def get_patient(pid: str):
    data = load_data()
    if pid not in data:
        raise HTTPException(404, "Patient not found")
    return Patient(**data[pid]).model_dump()

# POST add a new patient
@app.post("/patients")
def add_patient(patient: Patient):
    data = load_data()
    if patient.id in data:
        raise HTTPException(400, "Patient already exists")

    # save raw fields only
    data[patient.id] = patient.model_dump(exclude={"bmi", "verdict"})
    save_data(data)

    # return full record including computed fields
    return patient.model_dump()
