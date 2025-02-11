import os
import openai
import requests
from pymongo import MongoClient
from datetime import datetime, timedelta

# Load environment variables
MONGO_URI = os.getenv("MONGO_URI")
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client["parsed_content"]
collection = db["weather"]

# OpenAI API Setup
openai.api_key = OPENAI_API_KEY

def summarize_with_gpt(text):
    """Summarize text using OpenAI's GPT API."""
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a journalist providing engaging daily weather summaries."},
            {"role": "user", "content": f"Summarize today's weather updates in 2-3 sentences:\n\n{text}"}
        ]
    )
    return response['choices'][0]['message']['content']

def generate_daily_summary():
    """Retrieve weather data from MongoDB, summarize it, and send to Telegram."""
    since = datetime.utcnow() - timedelta(days=1)
    weather_entries = collection.find({"timestamp": {"$gte": since}})

    weather_texts = []
    for entry in weather_entries:
        weather_texts.append(f"{entry['timestamp'].strftime('%H:%M')} - {entry['description']}, {entry['temperature']}°C")

    if not weather_texts:
        print("⚠️ No weather data found for summarization.")
        return

    full_text = "\n".join(weather_texts)
    
    print(f"🔍 Raw text to summarize:\n{full_text}")  # Debugging Print

    summary = summarize_with_gpt(full_text)
    
    print(f"📝 GPT Summary Output:\n{summary}")  # Debugging Print

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    params = {"chat_id": CHANNEL_ID, "text": summary}
    requests.get(url, params=params)

    print(f"✅ Daily summary sent: {summary}")


if __name__ == "__main__":
    generate_daily_summary()
