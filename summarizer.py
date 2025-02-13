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
    print(f"🔍 Sending text to GPT: {text}", flush=True)

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a journalist providing engaging daily weather summaries."},
                {"role": "user", "content": f"Summarize today's weather updates in 2-3 sentences:\n\n{text}"}
            ]
        )

        print(f"📝 OpenAI Response: {response}", flush=True)
        return response['choices'][0]['message']['content']
    except Exception as e:
        print(f"❌ OpenAI Error: {e}", flush=True)
        return None

def generate_daily_summary():
    """Retrieve weather data from MongoDB, summarize it, and send to Telegram."""
    print("📌 Summarizer started.", flush=True)

    # Get weather data from the last 24 hours
    since = datetime.utcnow() - timedelta(days=1)
    weather_entries = list(collection.find({"timestamp": {"$gte": since}}))

    print(f"📊 Weather data retrieved: {len(weather_entries)} records", flush=True)

    if not weather_entries:
        print("⚠️ No weather data found for summarization.", flush=True)
        return

    weather_texts = [
        f"{entry['timestamp'].strftime('%H:%M')} - {entry['description']}, {entry['temperature']}°C"
        for entry in weather_entries
    ]
    
    full_text = "\n".join(weather_texts)
    
    print(f"📜 Full text for summarization:\n{full_text}", flush=True)

    summary = summarize_with_gpt(full_text)

    if not summary:
        print("⚠️ No summary generated.", flush=True)
        return

    print(f"✅ GPT Summary Output:\n{summary}", flush=True)

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    params = {"chat_id": CHANNEL_ID, "text": summary}
    response = requests.get(url, params=params)

    print(f"🚀 Telegram Response: {response.json()}", flush=True)

if __name__ == "__main__":
    generate_daily_summary()
