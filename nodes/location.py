from models import WeatherState


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