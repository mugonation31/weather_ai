from langgraph.graph import StateGraph, END
from typing import TypedDict
import requests

# Define the state that flows through our graph
class WeatherState(TypedDict):
    user_input: str
    location: str
    latitude: float
    longitude: float
    weather_data: dict
    recommendation: str
    final_response: str

# Node 1: Parse user input and extract location
def parse_location(state: WeatherState) -> WeatherState:
    user_input = state["user_input"]
    # Simple extraction - just take everything after "weather in"
    # We'll improve this later
    if "weather in" in user_input.lower():
        location = user_input.lower().split("weather in")[-1].strip()
    else:
        location = user_input.strip()
    
    state["location"] = location
    print(f"Extracted location: {location}")
    return state

# Add this new node after the parse_location function
def get_coordinates(state: WeatherState) -> WeatherState:
    location = state["location"]
    
    try:
        # Call OpenStreetMap Nominatim API
        url = f"https://nominatim.openstreetmap.org/search?q={location}&format=json&limit=1"
        headers = {'User-Agent': 'WeatherApp/1.0'}  # Required by Nominatim
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        
        if data:
            state["latitude"] = float(data[0]["lat"])
            state["longitude"] = float(data[0]["lon"])
            print(f"Found coordinates: {state['latitude']}, {state['longitude']}")
        else:
            print(f"Location '{location}' not found")
            state["latitude"] = 0.0
            state["longitude"] = 0.0
            
    except Exception as e:
        print(f"Error getting coordinates: {e}")
        state["latitude"] = 0.0
        state["longitude"] = 0.0
    
    return state

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

# Add this new node after the get_weather function
def make_recommendation(state: WeatherState) -> WeatherState:
    weather_data = state["weather_data"]
    location = state["location"]
    
    # Handle error cases
    if "error" in weather_data:
        state["recommendation"] = "Sorry, I couldn't get weather data for that location."
        state["final_response"] = state["recommendation"]
        return state
    
    # Get weather details
    temp = weather_data["temperature"]
    windspeed = weather_data["windspeed"]
    
    # Simple decision logic
    if temp >= 25:
        activity = "Great weather for outdoor activities! Maybe visit the beach or go for a walk."
    elif temp >= 15:
        activity = "Nice weather for exploring the city or having a coffee outside."
    elif temp >= 5:
        activity = "A bit cool - perfect for museums or indoor activities. Bring a jacket if going out."
    else:
        activity = "Pretty cold! Stay warm indoors or bundle up if you must go out."
    
    # Add wind consideration
    if windspeed > 20:
        activity += " It's quite windy though, so be prepared!"
    
    # Create recommendation
    recommendation = f"In {location.title()}, it's currently {temp}°C. {activity}"
    state["recommendation"] = recommendation
    state["final_response"] = recommendation
    
    print(f"Recommendation: {recommendation}")
    return state

# Create the graph
def create_weather_graph():
    workflow = StateGraph(WeatherState)
    
    # Add nodes
    workflow.add_node("parse_location", parse_location)
    workflow.add_node("get_coordinates", get_coordinates)
    workflow.add_node("get_weather", get_weather)
    workflow.add_node("make_recommendation", make_recommendation)
    
    # Set entry point
    workflow.set_entry_point("parse_location")
    
    # Connect nodes
    workflow.add_edge("parse_location", "get_coordinates")
    workflow.add_edge("get_coordinates", "get_weather")
    workflow.add_edge("get_weather", "make_recommendation")
    workflow.add_edge("make_recommendation", END)
    
    return workflow.compile()

# Test function
# Replace the existing test_basic function with this
def run_interactive():
    app = create_weather_graph()
    
    print("🌤️  Weather Recommendation Agent")
    print("Type a city name or 'quit' to exit")
    print("Examples: 'Malaga Spain', 'London', 'New York'")
    print("-" * 40)
    
    while True:
        user_input = input("\nEnter location: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("Goodbye! 👋")
            break
            
        if not user_input:
            print("Please enter a location!")
            continue
        
        try:
            # Create initial state
            initial_state = {
                "user_input": f"weather in {user_input}",
                "location": "",
                "latitude": 0.0,
                "longitude": 0.0,
                "weather_data": {},
                "recommendation": "",
                "final_response": ""
            }
            
            print(f"\n🔍 Looking up weather for: {user_input}")
            result = app.invoke(initial_state)
            
            print(f"\n✅ {result['final_response']}")
            
        except Exception as e:
            print(f"❌ Error: {e}")

# Update the main section
if __name__ == "__main__":
    run_interactive()