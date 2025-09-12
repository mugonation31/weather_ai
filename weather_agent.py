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

# Create the graph
def create_weather_graph():
    workflow = StateGraph(WeatherState)
    
    # Add nodes
    workflow.add_node("parse_location", parse_location)
    workflow.add_node("get_coordinates", get_coordinates)
    
    # Set entry point
    workflow.set_entry_point("parse_location")
    
    # Connect nodes
    workflow.add_edge("parse_location", "get_coordinates")
    workflow.add_edge("get_coordinates", END)
    
    return workflow.compile()

# Test function
def test_basic():
    app = create_weather_graph()
    
    # Test with sample input
    result = app.invoke({
        "user_input": "What's the weather in Malaga Spain",
        "location": "",
        "latitude": 0.0,
        "longitude": 0.0,
        "weather_data": {},
        "recommendation": "",
        "final_response": ""
    })
    
    print("Result:", result)

if __name__ == "__main__":
    test_basic()