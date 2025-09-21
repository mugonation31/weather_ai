from langgraph.graph import StateGraph, END
from nodes.location import parse_location
from nodes.geocoding import get_coordinates, get_coordinates
from nodes.weather import get_weather
from models import WeatherState
from config import llm, parser

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage   
import json  

# Load environment variables
load_dotenv()










# Replace the existing make_recommendation function with this
def make_recommendation(state: WeatherState) -> WeatherState:
    weather_data = state["weather_data"]
    location = state["location"]
    
    # Handle error cases
    if "error" in weather_data:
        state["recommendation"] = "Sorry, I couldn't get weather data for that location."
        state["final_response"] = state["recommendation"]
        state["parsed_recommendation"] = {}
        return state
    
    # Get weather details
    temp = weather_data["temperature"]
    windspeed = weather_data["windspeed"]
    
    try:
        # Create structured prompt for LLM
        prompt = f"""You are a weather assistant. Analyze the weather and provide a structured recommendation.

Location: {location.title()}
Temperature: {temp}°C
Wind Speed: {windspeed} km/h

{parser.get_format_instructions()}

Provide exactly one specific activity suggestion that's perfect for these conditions."""

        # Call LLM
        messages = [HumanMessage(content=prompt)]
        response = llm.invoke(messages)
        
        # Parse the structured output
        parsed_output = parser.parse(response.content)
        state["parsed_recommendation"] = parsed_output
        
        # Create a clean final response
        final_response = f"""📍 {location.title()} Weather Update:
🌡️ {parsed_output['condition_summary']} ({parsed_output['temperature']}°C)
🎯 Suggested Activity: {parsed_output['activity_suggestion']}
👕 What to Wear: {parsed_output['clothing_advice']}"""
        
        state["recommendation"] = response.content
        state["final_response"] = final_response
        
        print("Parsed JSON:", json.dumps(parsed_output, indent=2))
        
    except Exception as e:
        print(f"Parsing error: {e}")
        # Fallback
        fallback = {
            "condition_summary": f"Current weather in {location.title()}",
            "activity_suggestion": "Enjoy the outdoors" if temp > 15 else "Stay cozy indoors",
            "clothing_advice": "Dress appropriately for the temperature",
            "temperature": temp
        }
        state["parsed_recommendation"] = fallback
        state["final_response"] = f"Temperature: {temp}°C. {fallback['activity_suggestion']}"
    
    return state


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