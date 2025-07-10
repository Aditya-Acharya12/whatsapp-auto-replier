# WhatsApp Auto-Replier Bot 🤖💬

A Python-based WhatsApp automation bot that reads incoming messages using Selenium and replies with context-aware responses powered by Gemini Pro. Designed with a Gen-Z, sarcastic, and casual tone, the bot mimics the user’s texting personality using retrieval-augmented generation (RAG).

## 🔥 Features

- **Auto-read & reply** to WhatsApp Web messages
- **LLM-generated responses** via Gemini Pro API
- **Personality-mimicking** with Gen-Z tone & sarcasm
- **RAG-based context injection** using past chats
- **Selenium automation** for web interaction
- **Custom chat selector** for auto-targeting specific chats

## 🛠️ Tech Stack

- `Python`
- `Selenium`
- `Google Generative AI (Gemini)`
- `sentence-transformers`
- `NumPy`

## 🧠 How It Works

1. **Message Reading:** Selenium scrapes unread messages from selected WhatsApp chats.
2. **Contextual Retrieval:** Sentence-transformers embed the message and retrieve relevant past replies.
3. **Prompt Construction:** The message and past replies are used to craft a Gemini prompt with the user's unique tone.
4. **Response Generation:** Gemini generates a response, which is then typed and sent via Selenium.
5. **Fallback:** If Gemini fails, the bot uses rule-based templates to respond (optional/planned).

## 🤖 Personality Control

You can control the tone by adjusting the Gemini prompt to reflect your style. This includes avoiding punctuation, shortening sentences, and adopting sarcastic tones.

## 💡 Sample Prompt

> “Reply casually like Aditya. Use short lowercase sentences, don’t be formal or too polite. Avoid full stops and emojis unless necessary. You’re sarcastic but not rude. Avoid passive-aggression.”

## 🧪 Setup Instructions

1. **Clone the repo**
```bash
git clone https://github.com/your-username/whatsapp-auto-replier.git
cd whatsapp-auto-replier
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Add Gemini API Key**
```python
genai.configure(api_key="YOUR_API_KEY")
```

4. **Run the bot**
```bash
python bot.py
```

## ⚙️ Customization

- Add predefined chat names to auto-target
- Modify prompt logic for different personalities
- Connect to a MongoDB instance for persistent context storage

## 🚧 Future Improvements

- Toggleable CLI UI
- Background mode / hidden execution
- Rule-based fallbacks for Gemini errors
- Improved conversation logging & dashboard

## 📄 License

MIT License

---

> Built with way too much caffeine and personality ☕😎
