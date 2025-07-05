from dotenv import load_dotenv
import os
import json
import google.generativeai as genai
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Load environment variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# Gemini model
llm = genai.GenerativeModel("gemini-1.5-flash")  # You can swap with "gemini-pro" if needed

# Load precomputed data
with open("data/chat_chunks_embedded.json", "r", encoding="utf-8") as f:
    embedded_chunks = json.load(f)

# Load model
embed_model = SentenceTransformer("all-MiniLM-L6-v2")

# Keyword groups that deserve stronger tone
HYPE_KEYWORDS = ["ferrari", "ucl", "final", "heartbreak", "podium", "insane", "cracked", "clutch", "last minute"]

def is_emotional_trigger(text: str) -> bool:
    text = text.lower()
    return any(word in text for word in HYPE_KEYWORDS)

# Function to get reply using personality-chunk retrieval + Gemini generation
def get_llm_reply(message: str) -> str:
    try:
        # Embed incoming message
        query_embedding = embed_model.encode(message)

        # Compute similarities
        similarities = []
        for chunk in embedded_chunks:
            score = cosine_similarity(
                [query_embedding], [chunk["embedding"]]
            )[0][0]
            similarities.append((score, chunk["text"]))

        # Sort and get top 2-3 chunks
        top_chunks = [text for _, text in sorted(similarities, reverse=True)[:3]]

        # Add a stronger prompt if emotional topic is detected
        extra_flair = (
            "\nReact a bit stronger and emotionally if the message is about sports, heartbreaks, or intense topics."
            if is_emotional_trigger(message)
            else ""
        )

        # Create system prompt
        system_prompt = (
            "You are Aditya replying on WhatsApp. Your tone is casual, sarcastic, and chill, but not too over-the-top. "
            "Use short replies, lowercase slang, and keep it realistic — no excessive punctuation or excitement unless it’s hype-worthy."
            f"{extra_flair}\n\nHere are examples of how you usually talk:\n\n"
        )

        example_text = "\n---\n".join(top_chunks)
        final_input = f"{system_prompt}\n{example_text}\n\nNew message: {message}\n\nReply as Aditya:"

        # Call Gemini
        response = llm.generate_content(final_input)
        return response.text.strip()

    except Exception as e:
        print("LLM error:", e)
        return "bro idk that broke me 💀"
