import json
from sentence_transformers import SentenceTransformer

def main():
    with open("data/chat_chunks.json", "r", encoding="utf-8") as f:
        chunks = json.load(f)

    model = SentenceTransformer("all-MiniLM-L6-v2")

    for chunk in chunks:
        text = chunk["text"]
        embedding = model.encode(text)
        chunk["embedding"] = embedding.tolist()  # JSON-safe

    with open("data/chat_chunks_embedded.json", "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)

    print(f"Generated embeddings for {len(chunks)} chunks and saved to data/chat_chunks_embedded.json")

if __name__ == "__main__":
    main()