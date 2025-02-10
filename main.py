import os
import requests
from flask import Flask
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)

# Load environment variables
MONGO_URI = os.getenv("MONGO_URI")
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
CITY = os.getenv("CITY", "London")

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client["parsed_content"]
collection = db["weather"]

def get_weather():
    """Fetch weather data from OpenWeather API and store in MongoDB."""
    url = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={WEATHER_API_KEY}&units=metric"
    response = requests.get(url).json()

    if "weather" not in response or "main" not in response:
        return "⚠️ Error fetching weather data."

    # Prepare data for MongoDB
    weather_data = {
        "city": CITY,
        "description": response["weather"][0]["description"],
        "temperature": response["main"]["temp"],
        "timestamp": datetime.utcnow()
    }

    # Store in MongoDB
    collection.insert_one(weather_data)

    return f"🌤️ Weather in {CITY}: {response['weather'][0]['description']}, {response['main']['temp']}°C"

@app.route("/")
def send_weather_to_telegram():
    """Fetch weather and send to Telegram"""
    message = get_weather()
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    params = {"chat_id": CHANNEL_ID, "text": message}
    requests.get(url, params=params)
    return "Message Sent", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

