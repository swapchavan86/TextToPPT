import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=dotenv_path)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    print("Error: GOOGLE_API_KEY not found. Please ensure it's set in your .env file.")
else:
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
        print("Google Generative AI SDK configured successfully.")

        print("\nListing available Generative AI models:")
        found_any_models = False
        for m in genai.list_models():
            found_any_models = True
            print(f"  - Model: {m.name}, Supports: {m.supported_generation_methods}")

        if not found_any_models:
            print("No models found. This could indicate an API key issue, region restrictions, or no models available for this key.")

    except Exception as e:
        print(f"An error occurred during SDK configuration or model listing: {e}")