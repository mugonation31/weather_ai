from langgraph.graph import StateGraph, END
from typing import TypedDict
import requests
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI  
from langchain_core.messages import HumanMessage  

# Load environment variables
load_dotenv()

# Initialize LLM
llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0.7,
    api_key=os.getenv("OPENAI_API_KEY")
)

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

# Replace the existing make_recommendation function with this
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
    
    try:
        # Create prompt for LLM
        prompt = f"""You are a helpful weather assistant. Based on the current weather data, provide a friendly and practical recommendation.

Location: {location.title()}
Temperature: {temp}°C
Wind Speed: {windspeed} km/h

Please provide:
1. A brief comment on the current conditions
2. Activity suggestions appropriate for this weather
3. Any practical advice (clothing, etc.)

Keep the response conversational and under 100 words."""

        # Call LLM
        messages = [HumanMessage(content=prompt)]
        response = llm.invoke(messages)
        
        recommendation = response.content.strip()
        
        state["recommendation"] = recommendation
        state["final_response"] = recommendation
        
        print(f"LLM Recommendation: {recommendation}")
        
    except Exception as e:
        # Fallback to simple logic if LLM fails
        print(f"LLM error, using fallback: {e}")
        
        if temp >= 25:
            activity = "Great weather for outdoor activities!"
        elif temp >= 15:
            activity = "Nice weather for exploring."
        else:
            activity = "Cooler weather - dress warmly."
            
        recommendation = f"In {location.title()}, it's {temp}°C. {activity}"
        state["recommendation"] = recommendation
        state["final_response"] = recommendation
    
    return state

# Add Error Handling & Conditional Routing
def check_coordinates(state: WeatherState) -> str:
    """Conditional function to decide next step based on coordinates"""
    if state["latitude"] == 0.0 and state["longitude"] == 0.0:
        return "handle_error"
    else:
        return "get_weather"

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

# Create the graph
def create_weather_graph():
    workflow = StateGraph(WeatherState)
    
    # Add all nodes
    workflow.add_node("parse_location", parse_location)
    workflow.add_node("get_coordinates", get_coordinates)
    workflow.add_node("get_weather", get_weather)
    workflow.add_node("make_recommendation", make_recommendation)
    workflow.add_node("handle_error", handle_error)  # Add error handler
    
    # Set entry point
    workflow.set_entry_point("parse_location")
    
    # Connect nodes with conditional routing
    workflow.add_edge("parse_location", "get_coordinates")
    
    # Conditional edge based on coordinates
    workflow.add_conditional_edges(
        "get_coordinates",
        check_coordinates,  # Function that decides the path
        {
            "get_weather": "get_weather",      # If coordinates found
            "handle_error": "handle_error"     # If coordinates not found
        }
    )
    
    workflow.add_edge("get_weather", "make_recommendation")
    workflow.add_edge("make_recommendation", END)
    workflow.add_edge("handle_error", END)  # Error path also ends
    
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
                "final_response": "",
                "parsed_recommendation": {}  
            }
            
            print(f"\n🔍 Looking up weather for: {user_input}")
            result = app.invoke(initial_state)
            
            print(f"\n✅ {result['final_response']}")
            
        except Exception as e:
            print(f"❌ Error: {e}")

# Test OpenAI (add this anywhere in your code)
try:
    response = llm.invoke([HumanMessage(content="Say 'OpenAI is working!'")])
    print(f"🤖 OpenAI: {response.content}")
except Exception as e:
    print(f"❌ OpenAI Error: {e}")

# Update the main section
if __name__ == "__main__":
    run_interactive()