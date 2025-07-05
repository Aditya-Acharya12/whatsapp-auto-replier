import json
from typing import List, Dict
import os

# Token estimation helper
def estimate_tokens(text: str) -> int:
    return len(text.split())  # Approximate (can use tiktoken for precision)

def chunk_messages(messages, chunk_size=500, overlap=50):
    chunks = []
    current_chunk = ""

    for msg in messages:
        if "speaker" not in msg or "text" not in msg:
            continue  # skip malformed entries

        msg_text = f"{msg['speaker']}: {msg['text']}"
        if len(current_chunk) + len(msg_text) + 1 <= chunk_size:
            current_chunk += msg_text + "\n"
        else:
            chunks.append(current_chunk.strip())
            current_chunk = msg_text + "\n"

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks

def main():
    input_path = "data/chat_data.json"
    output_path = "data/chat_chunks.json"

    if not os.path.exists(input_path):
        raise FileNotFoundError(f"{input_path} does not exist.")

    with open("data/chat_data.json", "r", encoding="utf-8") as f:
        messages = json.load(f)

    chunks = chunk_messages(messages)

    with open("data/chat_chunks.json", "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)


    print(f"Chunked {len(messages)} messages into {len(chunks)} chunks.")
    print(f"Saved chunks to {output_path}")

if __name__ == "__main__":
    main()
