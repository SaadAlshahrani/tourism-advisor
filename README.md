# Trip Advisor
A small project where an LLM, given weather information for and points of interest in a destination, describes that destination in a creative way to help users decide whether to make plans to go there.

The project uses:
1. Google Gemini 2.0 Flash as its LLM
2. LangChain
3. OpenCage Geocoding API for retrieving location coordinates
4. tomorrow.io API for retrieving weather information for that location
5. FourSquare places API for retrieving points of interest near the location

# TODO
- Create a simple UI for the project
- Serve the project through the cloud. Most likely Google Cloud will be used
- Containerize the application with Docker
- Track LLM with MLFlow