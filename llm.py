from dotenv import load_dotenv
import os
import json
import google.generativeai as genai
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import re

# Load environment variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# Gemini model
llm = genai.GenerativeModel("gemini-1.5-flash")

# Load embeddings
with open("data/chat_chunks_embedded.json", "r", encoding="utf-8") as f:
    embedded_chunks = json.load(f)

# Load embedding model
embed_model = SentenceTransformer("all-MiniLM-L6-v2")

# High-emotion keywords
HYPE_KEYWORDS = ["ferrari", "ucl", "final", "heartbreak", "podium", "insane", "cracked", "clutch", "last minute"]

# 🧠 Fallback keyword-based rules
FALLBACK_RULES = {
    "where": "probably home or dead inside idk",
    "exam": "pls don’t remind me",
    "race": "yea hoping ferrari doesn't fumble for once",
    "coming back": "soon bro chill",
    "college": "ugh starting soon i think",
    "food": "starving actually",
    "movie": "i’m down, when?",
    "location": "i ain’t disclosing that here lol",
    "test": "yo why u testing me 💀",
    "how are you": "eh existing i guess",
    "semester": "don’t ask bruh"
}

# Smart match fallback
def rule_based_reply(message: str) -> str:
    msg = message.lower()
    for keyword, reply in FALLBACK_RULES.items():
        if keyword in msg:
            return reply
    return "lol idk bro"  # generic fallback

def is_emotional_trigger(text: str) -> bool:
    return any(word in text.lower() for word in HYPE_KEYWORDS)

# Clean Gemini response to match your style
def sanitize_reply(reply: str) -> str:
    reply = reply.strip()
    reply = re.sub(r'(?<!\w)\.(?!\w)', '', reply)  # remove full stops unless in words
    reply = re.sub(r'\s{2,}', ' ', reply)
    return reply.lower()

def get_llm_reply(message: str, context: str = "") -> str:
    try:
        # Embed the incoming message
        query_embedding = embed_model.encode(message)

        # Compute similarity with your chunks
        similarities = []
        for chunk in embedded_chunks:
            score = cosine_similarity([query_embedding], [chunk["embedding"]])[0][0]
            similarities.append((score, chunk["text"]))

        # Get top 2–3 similar chunks
        top_chunks = [text for _, text in sorted(similarities, reverse=True)[:3]]

        # System prompt
        system_prompt = (
            "You are Aditya replying on WhatsApp.\n"
            "You're chill, sarcastic when needed, but never overly tryhard. Your messages are:\n"
            "- Always lowercase\n"
            "- Never use full stops (.) at the end of sentences\n"
            "- Prefer casual contractions like 'idk', 'nah', 'tbh', 'yea', 'lemme', etc.\n"
            "- Often dry, witty, sometimes emotionally flat — unless the topic is hype-worthy (like F1, heartbreak, exams)\n"
            "- Short and context-aware. Usually 1–2 lines max unless the situation needs more.\n"
            "- You never force emojis especially ♂️, but you’ll throw in a 😭 or 💀 if it fits naturally\n"
            "- You don't repeat words or fake energy — you're effortlessly sarcastic, not over the top\n\n"
            "Below are real examples of how Aditya texts. Match this tone exactly:\n\n"
        )

        # Example text from retrieved chunks
        example_text = ""
        for i, chunk in enumerate(top_chunks):
            example_text += f"Example {i+1}:\n{chunk.strip()}\n\n"

        # Add emotional note if it's a hyped topic
        emotional_note = (
            "If the message is about grades or academics, sports, hype, or heartbreak, react naturally — maybe more energy or sarcasm.\n"
            if is_emotional_trigger(message) else ""
        )

        final_input = (
            f"{system_prompt}{example_text}"
            f"{emotional_note}"
            f"Context (last few messages):\n{context}\n\n"
            f"Incoming message: {message}\n\n"
            f"Now reply like Aditya:"
        )

        # Gemini response
        response = llm.generate_content(final_input)
        return sanitize_reply(response.text)

    except Exception as e:
        print("LLM error:", e)
        print("⚠️ Using fallback rule-based reply.")
        return rule_based_reply(message)
