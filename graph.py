from langgraph.graph import StateGraph, END
from models import WeatherState
from nodes.location import parse_location
from nodes.geocoding import get_coordinates, check_coordinates
from nodes.weather import get_weather
from nodes.error_handling import handle_error
from nodes.recommendations import make_recommendation


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