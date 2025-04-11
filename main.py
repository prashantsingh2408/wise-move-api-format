from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware  # Import CORS middleware
import os
import chat_context_api
from typing import Optional

app = FastAPI()

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, specify exact origins instead of "*"
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
)

@app.post("/chat_content_api")
async def chat_content_api(user_message: str, system_prompt: Optional[str] = None):
    """
    Expected format: \n
    Request Body: \n
    user_message (str): \n
        <CHAT> \n
        USER: hi \n
        </CHAT> \n
        <CONTENT> \n
        Profile: \n
        </CONTENT> \n

    Expected Response: \n
        <CHAT>   \n
        USER: Hi   \n
        BOT: Hi! How are you? What is your name?  \n
        </CHAT>  \n
        <CONTENT>  \n
        Profile:  \n
        </CONTENT>  \n
    """
    try:
        response = chat_context_api.chat_content_api(user_message, system_prompt)
        return {
            "status": "success",
            "response": response
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/")
async def root():
    return {"message": "Welcome to the API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/test_groq_get")
async def test_groq_get(query: str):
    try:
        response = chat_context_api.test_groq_get(query)
        return {
            "status": "success",
            "response": response
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
  