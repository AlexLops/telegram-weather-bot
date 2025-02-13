import os
import openai
import requests
from pymongo import MongoClient
from datetime import datetime, timedelta

# Log file for debugging
LOG_FILE = "/tmp/summarizer_debug.log"

def log_message(message):
    """Log messages to both console (Render logs) and a file."""
    with open(LOG_FILE, "a") as log:
        log.write(message + "\n")
    print(message, flush=True)  # Ensure logs appear in Render

log_message("✅ Summarizer script started execution.")

# Load environment variables
MONGO_URI = os.getenv("MONGO_URI")
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    log_message("❌ OpenAI API key is missing. Exiting summarizer.")
    exit(1)

# Connect to MongoDB
try:
    client = MongoClient(MONGO_URI)
    db = client["parsed_content"]
    collection = db["weather"]
    log_message("✅ Connected to MongoDB successfully.")
except Exception as e:
    log_message(f"❌ MongoDB Connection Error: {e}")
    exit(1)

# OpenAI API Setup (New Client Syntax)
client = openai.OpenAI(api_key=OPENAI_API_KEY)

def summarize_with_gpt(text):
    """Summarize text using OpenAI's new API format."""
    log_message(f"🔍 Sending text to GPT: {text[:100]}...")  # Log first 100 chars

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a journalist providing engaging daily weather summaries."},
                {"role": "user", "content": f"Summarize today's weather updates in 2-3 sentences:\n\n{text}"}
            ]
        )

        summary = response.choices[0].message.content
        log_message(f"📝 GPT Summary Output:\n{summary}")
        return summary
    except Exception as e:
        log_message(f"❌ OpenAI Error: {e}")
        return None

def generate_daily_summary():
    """Retrieve weather data from MongoDB, summarize it, and send to Telegram."""
    log_message("📌 Summarizer started.")

    # Get weather data from the last 24 hours
    since = datetime.utcnow() - timedelta(days=1)
    weather_entries = list(collection.find({"timestamp": {"$gte": since}}))

    log_message(f"📊 Weather data retrieved: {len(weather_entries)} records")

    if not weather_entries:
        log_message("⚠️ No weather data found for summarization.")
        return

    # Compile weather descriptions
    weather_texts = [
        f"{entry['timestamp'].strftime('%H:%M')} - {entry['description']}, {entry['temperature']}°C"
        for entry in weather_entries
    ]
    
    full_text = "\n".join(weather_texts)
    
    log_message(f"📜 Full text for summarization:\n{full_text}")

    summary = summarize_with_gpt(full_text)

    if not summary:
        log_message("⚠️ No summary generated.")
        return

    log_message(f"✅ GPT Summary Output:\n{summary}")

    # Send summary to Telegram
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    params = {"chat_id": CHANNEL_ID, "text": summary}
    
    try:
        response = requests.get(url, params=params)
        log_message(f"🚀 Telegram Response: {response.json()}")
    except Exception as e:
        log_message(f"❌ Telegram API Error: {e}")

log_message("✅ Summarizer script finished execution.")

if __name__ == "__main__":
    generate_daily_summary()
