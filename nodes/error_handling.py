from models import WeatherState


def handle_error(state: WeatherState) -> WeatherState:
    """Handle cases where location wasn't found"""
    location = state["location"]
    
    error_msg = f"Sorry, I couldn't find '{location}'. Please try:"
    error_msg += "\n• A major city name (e.g., 'London')"
    error_msg += "\n• City with country (e.g., 'Paris France')"
    error_msg += "\n• Check spelling and try again"
    
    state["recommendation"] = error_msg
    state["final_response"] = error_msg
    
    print(f"Error handled: Location '{location}' not found")
    return state