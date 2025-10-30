# Import all libraries/modules
import re
import speech_recognition as sr
from gtts import gTTS
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from scipy.special import softmax
from openai import OpenAI
import os
import pygame

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key = ""
)

MODEL_NAME = "google/gemini-2.0-flash-exp:free"


def speak(text):
    # Convert text to speech and save
    tts = gTTS(text=text, lang="en")
    filename = "temp_reply.mp3"
    tts.save(filename)

    # Initialize pygame mixer
    pygame.mixer.init()
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()

    # Wait until the audio is done playing
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

    # Unload the file so it's not locked
    pygame.mixer.music.unload()

    # Remove file after playing
    os.remove(filename)


sent_tokenizer = AutoTokenizer.from_pretrained("cardiffnlp/twitter-roberta-base-sentiment")
sent_model = AutoModelForSequenceClassification.from_pretrained("cardiffnlp/twitter-roberta-base-sentiment")

def get_sentiment(user_text):
    user_text = re.sub(r"http\S+|www\S+|https\S+", "", user_text)
    user_text = re.sub(r"\@\w+|\#", "", user_text).strip()

    encoded = sent_tokenizer(user_text, return_tensors='pt')
    output = sent_model(**encoded)
    scores = softmax(output.logits[0].detach().numpy())
    scores_dict = {'Negative': scores[0], 'Neutral': scores[1], 'Positive': scores[2]}
    dominant = max(scores_dict, key=scores_dict.get)
    confidence = scores_dict[dominant]
    if confidence < 0.55:
        dominant = "Neutral"
    return dominant


def get_llm_reply(user_text, sentiment):
    sentiment_mapping = {
        "Negative": "feeling sad or upset",
        "Neutral": "feeling okay or neutral",
        "Positive": "feeling happy or content"
    }

    prompt = f"""
The user said: "{user_text}".
They are {sentiment_mapping[sentiment]}.
Respond as a compassionate therapist in a empathetic, and supportive way. Don't use metaphors, and speak in an easy to understand way. Keep it short, max 1-2 sentences.
"""

    completion = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}]
    )

    return completion.choices[0].message.content

def get_llm_reply(user_text, sentiment):
    sentiment_mapping = {
        "Negative": "feeling sad or upset",
        "Neutral": "feeling okay or neutral",
        "Positive": "feeling happy or content"
    }

    prompt = f"""
The user said: "{user_text}".
They are {sentiment_mapping[sentiment]}.
Respond as a compassionate therapist in an empathetic, and supportive way. 
Don't use metaphors, and speak in an easy to understand way. Keep it short, max 2-3 sentences.
"""

    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}]
        )
        return completion.choices[0].message.content

    except Exception as e:
        if "429" in str(e):
            return "I'm really sorry, but I'm getting too many requests right now. Could you please try again in a moment?"
        else:
            return f"Something went wrong: {e}"



def run_therapist_bot():
    print("Therapist Bot started. Say 'quit' to exit.")
    while True:
        user_text = get_user_speech()
        if not user_text:
            continue
        if user_text.lower() in ["quit", "exit"]:
            break

        sentiment = get_sentiment(user_text)
        reply = get_llm_reply(user_text, sentiment)
        print("Therapist:", reply)
        speak(reply)



if __name__ == "__main__":
    run_therapist_bot()