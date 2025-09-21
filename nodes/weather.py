import requests
from models import WeatherState

# Add this new node after the get_coordinates function
def get_weather(state: WeatherState) -> WeatherState:
    latitude = state["latitude"]
    longitude = state["longitude"]
    
    # Skip if we don't have valid coordinates
    if latitude == 0.0 and longitude == 0.0:
        state["weather_data"] = {"error": "No valid coordinates"}
        return state
    
    try:
        # Call OpenMeteo API
        url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current_weather=true&timezone=auto"
        
        response = requests.get(url)
        response.raise_for_status()
        
        data = response.json()
        state["weather_data"] = data["current_weather"]
        
        # Print weather info for testing
        weather = data["current_weather"]
        temp = weather["temperature"]
        windspeed = weather["windspeed"]
        print(f"Weather: {temp}°C, Wind: {windspeed} km/h")
        
    except Exception as e:
        print(f"Error getting weather: {e}")
        state["weather_data"] = {"error": str(e)}
    
    return state