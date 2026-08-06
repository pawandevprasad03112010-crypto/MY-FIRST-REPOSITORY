import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# CORS इनेबल करें ताकि फ्लटर ऐप से रिक्वेस्ट आसानी से आ सके
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# लॉगिन डेटा मॉडल
class LoginRequest(BaseModel):
    email: str
    password: str

# आपका डमी यूज़र डेटा
MOCK_USER = {
    "email": "ppawandevprasad@gmail.com",
    "password": "password123",
    "name": "PAWAN DEV PRASAD"
}

@app.post("/api/login")
def login(data: LoginRequest):
    if data.email == MOCK_USER["email"] and data.password == MOCK_USER["password"]:
        return {
            "status": "success",
            "message": "Login Successful",
            "name": MOCK_USER["name"],
            "email": MOCK_USER["email"]
        }
    else:
        raise HTTPException(status_code=400, detail="गलत ईमेल या पासवर्ड!")

# Render पर होस्टिंग के लिए डायनेमिक पोर्ट सेटअप
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
    
