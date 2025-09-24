from graph import create_weather_graph



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


# Update the main section
if __name__ == "__main__":
    run_interactive()