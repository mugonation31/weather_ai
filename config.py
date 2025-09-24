import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI  
from langchain_core.output_parsers import JsonOutputParser  
from models import WeatherRecommendation

# Load environment variables
load_dotenv()


# Initialize LLM
llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0.7,
    api_key=os.getenv("OPENAI_API_KEY")
)



# Create parser
parser = JsonOutputParser(pydantic_object=WeatherRecommendation)


