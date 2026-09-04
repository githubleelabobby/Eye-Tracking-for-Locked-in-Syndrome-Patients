from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Stores the latest patient request
latest_request = None


class PatientRequest(BaseModel):
    need: str


@app.get("/")
def home():
    return {"message": "Eye-Gaze Assistive App Backend is Running!"}


# Receives request from patient webpage
@app.post("/request")
def receive_request(request: PatientRequest):

    global latest_request

    latest_request = request.need

    print("Patient requested:", latest_request)

    return {
        "message": "Request received successfully",
        "need": latest_request
    }


# Sends latest request to caregiver webpage
@app.get("/latest-request")
def get_latest_request():

    return {
        "need": latest_request
    }
@app.post("/acknowledge")
def acknowledge_request():

    global latest_request

    latest_request = None

    print("Request acknowledged")

    return {
        "message": "Request acknowledged successfully"
    }