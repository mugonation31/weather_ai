import json 
import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage   
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser
from models import WeatherState, WeatherRecommendation

# Load environment and create fresh LLM instance
load_dotenv()
llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0.7,
    api_key=os.getenv("OPENAI_API_KEY")
)
parser = JsonOutputParser(pydantic_object=WeatherRecommendation)

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
        print("🔧 Creating prompt...")
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
        print(f"LLM error: {e}")
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