# test_server.py
import httpx

# --- Round 2 Test Payload ---
test_payload = {
    "email": "student@example.com",
    "secret": "Project-server", # Make sure this matches your .env
    "task": "final-build-test", # KEEP THE SAME TASK ID
    "round": 2, # Set to 2 for the revise test
    "nonce": "round-2-nonce-final",
    # ⬇️ THIS IS THE CORRECT BRIEF FOR THE REVISION
    "brief": "Update the page. Add a new section below the paragraph with a list of the tools used in this project: FastAPI, Google Gemini, and GitHub.",
    "checks": [],
    "evaluation_url": "https://example.com/notify",
    "attachments": []
}

try:
    print("--- 🚀 RUNNING ROUND 2 (REVISE) TEST ---")
    response = httpx.post("http://127.0.0.1:8000/handle-task", json=test_payload)
    response.raise_for_status()
    print("✅ Success! Server responded with:")
    print(response.json())
except httpx.HTTPStatusError as e:
    print(f"❌ Error! Server responded with status {e.response.status_code}:")
    print(e.response.json())
except httpx.RequestError as e:
    print(f"❌ Request Error! Could not connect to the server: {e}")