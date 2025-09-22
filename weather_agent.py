from langgraph.graph import StateGraph, END
from nodes.location import parse_location
from nodes.geocoding import get_coordinates, check_coordinates
from nodes.weather import get_weather
from nodes.error_handling import handle_error
from nodes.recommendations import make_recommendation
from graph import create_weather_graph
from models import WeatherState


from dotenv import load_dotenv
 

# Load environment variables
load_dotenv()


















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