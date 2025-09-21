from models import WeatherState
import requests


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

# Add Error Handling & Conditional Routing
def check_coordinates(state: WeatherState) -> str:
    """Conditional function to decide next step based on coordinates"""
    if state["latitude"] == 0.0 and state["longitude"] == 0.0:
        return "handle_error"
    else:
        return "get_weather"
