# Therapist Bot

Therapist Bot is an AI-powered, voice-based chatbot that listens to user speech, analyzes sentiment, and responds empathetically. It creates an interactive therapy-like experience using natural language understanding and text-to-speech technology.

---

## Features
- **Real-time speech recognition** using `speech_recognition`.
- **Sentiment analysis** of user speech using `transformers` and CardiffNLP's RoBERTa model.
- **AI-generated empathetic responses** via the Deepseek LLaMA model on OpenRouter/OpenAI API.
- **Text-to-speech output** using `gTTS` and playback with `pygame`.
- Handles ambiguous sentiment with confidence thresholds and responds supportively.

---

## Skills & Technologies Used
- **Python programming**
- **Speech recognition & audio processing** (`speech_recognition`, `pygame`)
- **Natural Language Processing (NLP)** (`transformers`, sentiment classification)
- **Text-to-Speech (TTS)** (`gTTS`)
- **API integration** (OpenAI / Deepseek LLaMA)
- **Regular expressions** for text cleaning
- **Softmax & probability handling** for sentiment confidence

---

## Lessons Learned
- How to integrate **speech-to-text** and **text-to-speech** in Python.
- Sentiment analysis challenges and the importance of **confidence thresholds**.
- How to structure **prompts for an LLM** to produce empathetic, human-like responses.
- Handling **temporary audio files** and managing system resources with `pygame`.
- Combining multiple AI models in a single pipeline for a complete interactive experience.

---

## Future Improvements / Features to Add
- Add **conversation history** to make responses more context-aware.
- Improve **speech recognition accuracy** with noise reduction techniques.
- Allow users to **choose voice types or languages** for TTS.
- Add a **GUI interface** for easier interaction.
- Implement **emotional tone tracking** to better adapt responses over time.
- Add **logging and analytics** to track sentiment trends in conversations.
- Potentially integrate **real-time feedback** or mental health tips.

---

## Requirements
- Python 3.10+
- Install dependencies:

```bash
pip install re speechrecognition gTTS transformers scipy openai pygame
