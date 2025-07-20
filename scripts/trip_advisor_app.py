import requests
import os

import streamlit as st

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.prompts import PromptTemplate
from langgraph.graph import START, StateGraph
from typing_extensions import TypedDict

# Environment variables
# load_dotenv()

# State class for LangChain Graph
class State(TypedDict):
    query: str
    location: str
    location_information: str
    answer: str

# APIs
# geocoding_uri = 'https://nominatim.openstreetmap.org/search'
GEOCODE_URI = 'https://api.opencagedata.com/geocode/v1/json'
WEATHER_URI = 'https://api.tomorrow.io/v4/weather/forecast'
POI_URI = 'https://places-api.foursquare.com/places/search'

# Initialize LLM and custom prompts
llm = init_chat_model('gemini-2.0-flash', model_provider='google_genai')
location_prompt = PromptTemplate.from_template('Your task is to extract the location from a user query.\nQuery: {query}\nLocation: ')
describe_prompt = PromptTemplate.from_template("You are an assistant for giving rich descriptions on locations and cities around the world for tourism. Using your knowledge base, and given the following weather information and at most 3 points of interest chosen at your discretion in that location, give a rich description of the location. Be creative.\nLocation: {location}\nLocation information: {location_information}\nAnswer:")

# Helper function to extract destionation name
def extract_city(state: State):
    extraction_prompt = location_prompt.invoke({'query': state['query']})
    response = llm.invoke(extraction_prompt)
    return {'location': response.content}

# Retrieve information from APIs
def retrieve_location_info(state: State):
    # Retrieve latitude and longtitude from geocode api
    destination = state['location']
    geo_response = requests.get(GEOCODE_URI, params={'q': destination, 'key': os.environ['OPENCAGE_API_KEY']})
    lat = geo_response.json()['results'][0]['geometry']['lat']
    lon = geo_response.json()['results'][0]['geometry']['lng']

    # Retrieve weather information from coordinates
    weather_headers = {
    "accept": "application/json",
    "accept-encoding": "deflate, gzip, br"
    }
    weather_query = f"{lat},{lon}"
    weather_response = requests.get(WEATHER_URI, headers=weather_headers, params={'location': weather_query, 'apikey': os.environ['WEATHER_API_KEY']})
    
    weather_str = ['Weather Information for This Location for the Next 6 Days: \n\n']
    for day in weather_response.json()['timelines']['daily']:
        weather_str.append(f"{day['time'][:10]} | Max Temp: {day['values']['temperatureMax']}°C | Feels Like: {day['values']['temperatureApparentMax']}°C\n"
        f"Avg Humidity: {day['values']['humidityAvg']}%\n"
        f"Rain Probability: {day['values']['precipitationProbabilityMax']}%\n\n")
    weather_str = ''.join(weather_str)
        
    # Retrieve POI information from coordinates
    poi_headers = {
    "accept": "application/json",
    "X-Places-Api-Version": "2025-06-17",
    "authorization": f"Bearer {os.environ['POI_API_KEY']}"
    }
    category_ids = '4bf58dd8d48988d182941735,4bf58dd8d48988d181941735,4d4b7105d754a06377d81259'
    poi_response = requests.get(POI_URI, headers=poi_headers, params={'ll': weather_query, 'radius': 100000, 'fsq_category_ids': category_ids, 'fields': 'name,categories,location', 'limit': 20})

    poi_str = ['Points of Interest in This Location: \n\n']
    for location in poi_response.json()['results']:
        poi_str.append(f"POI Type: {location['categories'][0]['name']}\n"
        f"Name: {location['name']}\n"
        f"Address: {location['location']['formatted_address']}\n\n")
    poi_str = ''.join(poi_str)
    
    # Concatenate and return full information
    return {'location_information': ''.join([weather_str, poi_str])}

# Generate LLM response
def generate(state: State):
    messages = describe_prompt.invoke({'location': state['location'], 'location_information': state['location_information']})
    response = llm.invoke(messages)
    return {'answer': response.content}

# Create graph workflow
graph_builder = StateGraph(State).add_sequence([extract_city, retrieve_location_info, generate])
graph_builder.add_edge(START, 'extract_city')
graph = graph_builder.compile() 

# Streamlit app
st.set_page_config(
    page_title="Trip Advisor",
    page_icon="🗺️",
)

st.title('Trip Advisor')

user_input = st.text_input('Which destination do you want to learn about?')

if st.button("Let's go!"):
    if not user_input.strip():
        st.warning("Please enter a location.")
    else:
        with st.spinner("Retrieving information and generating response..."):
            try:
                result = graph.invoke({'query': user_input})
                st.success("Here's what we found:")
                st.markdown(result['answer'])
            except Exception as e:
                st.error(f"Something went wrong: {str(e)}")