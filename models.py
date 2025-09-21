from typing import TypedDict
from langchain_core.output_parsers import JsonOutputParser  
from pydantic import BaseModel, Field


# Define the state that flows through our graph
class WeatherState(TypedDict):
    user_input: str
    location: str
    latitude: float
    longitude: float
    weather_data: dict
    recommendation: str
    final_response: str
    parsed_recommendation: dict

# Define the structured output format
class WeatherRecommendation(BaseModel):
    condition_summary: str = Field(description="Brief summary of current weather conditions")
    activity_suggestion: str = Field(description="One specific activity recommendation")
    clothing_advice: str = Field(description="What to wear for this weather")
    temperature: float = Field(description="Current temperature in Celsius")