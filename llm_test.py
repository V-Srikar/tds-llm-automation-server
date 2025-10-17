# llm_test.py
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load the .env file to get our API key
load_dotenv()

print("--- Starting direct Gemini API test ---")

try:
    # Configure the API key
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

    # Create the model instance
    model = genai.GenerativeModel('gemini-pro-latest')

    print("Model configured. Calling the API now... (This may take a moment)")

    # Make the API call
    response = model.generate_content("What is 2 + 2?")

    print("✅ Success! API responded.")
    print("Response from Gemini:")
    print(response.text)

except Exception as e:
    print(f"❌ An error occurred: {e}")

print("--- Test finished ---")
