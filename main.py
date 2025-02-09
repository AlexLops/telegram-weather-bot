import requests
import os
from flask import Flask

app = Flask(__name__)

# API Credentials (Set these in Railway)
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
CITY = os.getenv("CITY", "London")

def get_weather():
    """Fetch weather data from OpenWeather API"""
    url = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={WEATHER_API_KEY}&units=metric"
    response = requests.get(url).json()
    return f"🌤️ Weather in {CITY}: {response['weather'][0]['description']}, {response['main']['temp']}°C"

@app.route("/")
def send_weather_to_telegram():
    """Sends weather updates to Telegram"""
    message = get_weather()
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    params = {"chat_id": CHANNEL_ID, "text": message}
    requests.get(url, params=params)
    return "Message Sent", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
