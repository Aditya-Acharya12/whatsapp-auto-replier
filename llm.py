from dotenv import load_dotenv
import os
import google.generativeai as genai

# Load environment variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# Configure Gemini
genai.configure(api_key=api_key)
llm = genai.GenerativeModel("gemini-2.5-flash")

# Function to get a reply from the model
def get_llm_reply(message):
    try:
        response = llm.generate_content(message)
        return response.text.strip()
    except Exception as e:
        print("LLM error:", e)
        return "Sorry, I couldn't generate a reply."