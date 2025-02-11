import os
import requests
from pymongo import MongoClient
from datetime import datetime

# Load environment variables
MONGO_URI = os.getenv("MONGO_URI")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
CITY = os.getenv("CITY", "London")

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client["parsed_content"]
collection = db["weather"]

def fetch_weather():
    """Fetch weather data and store it in MongoDB."""
    url = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={WEATHER_API_KEY}&units=metric"
    response = requests.get(url).json()

    if "weather" not in response or "main" not in response:
        print("⚠️ Error fetching weather data.")
        return None

    # Prepare raw weather data
    weather_data = {
        "city": CITY,
        "description": response["weather"][0]["description"],
        "temperature": response["main"]["temp"],
        "timestamp": datetime.utcnow()
    }

    # Store in MongoDB
    collection.insert_one(weather_data)
    print(f"✅ Weather data stored: {weather_data}")

if __name__ == "__main__":
    fetch_weather()
