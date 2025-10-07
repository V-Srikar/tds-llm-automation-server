from fastapi import FastAPI, Request, HTTPException
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Create a FastAPI application instance
app = FastAPI()

# Retrieve your secret from the environment variables
MY_PROJECT_SECRET = os.getenv("MY_PROJECT_SECRET")

@app.post("/handle-task")
async def handle_task_request(request: Request):
    data = await request.json()

    if data.get('secret') != MY_PROJECT_SECRET:
        raise HTTPException(status_code=403, detail="Invalid secret")

    print("Received a valid request:")
    print(data)

    return {"message": "Request received and secret validated successfully."}
