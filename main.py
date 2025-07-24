import os
from dotenv import load_dotenv
import chainlit as cl
import requests

# Load environment variables
load_dotenv()
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

# Verify API key
if not WEATHER_API_KEY:
    raise ValueError("WEATHER_API_KEY is not set in the .env file")

# Function to fetch weather data from WeatherAPI
async def get_weather_data(city):
    url = f"http://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q={city}&aqi=no"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return {
            "city": data["location"]["name"],
            "country": data["location"]["country"],
            "temp_c": data["current"]["temp_c"],
            "temp_f": data["current"]["temp_f"],
            "condition": data["current"]["condition"]["text"],
            "wind_mph": data["current"]["wind_mph"],
            "wind_dir": data["current"]["wind_dir"]
        }
    except requests.RequestException as e:
        return {"error": f"Failed to fetch weather data: {str(e)}"}

# Show greeting on chat start
@cl.on_chat_start
async def on_chat_start():
    await cl.Message(content="🌤️ Welcome! I am your Weather Assistant!\n\n🤔 How can I assist you with the weather today? (e.g., current weather in London)").send()

# Handle user questions
@cl.on_message
async def handle_message(message: cl.Message):
    # Extract city from input
    city = None
    words = message.content.lower().split()
    for i, word in enumerate(words):
        if word in ["in", "for", "at"] and i + 1 < len(words):
            city = " ".join(words[i + 1:i + 3]).capitalize()  # Handle multi-word cities
            break
    if not city:
        await cl.Message(content="Please specify a city, e.g., 'weather in London'.").send()
        return
    # Fetch weather data
    weather_data = await get_weather_data(city)
    if "error" in weather_data:
        await cl.Message(content=weather_data["error"]).send()
        return
    # Format response
    response = (
        f"It's currently {weather_data['temp_f']}°F ({weather_data['temp_c']}°C) in {weather_data['city']}, {weather_data['country']} "
        f"with {weather_data['condition'].lower()} skies. Winds are from the {weather_data['wind_dir']} at {weather_data['wind_mph']} mph."
    )
    await cl.Message(content=response).send()