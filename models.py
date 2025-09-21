from typing import TypedDict
from langchain_core.output_parsers import JsonOutputParser  
from langchain_core.pydantic_v1 import BaseModel, Field  


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