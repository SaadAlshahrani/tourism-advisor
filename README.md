# Trip Advisor
A small project where an LLM, given weather information for and points of interest in a destination, describes that destination in a creative way to help users decide whether to make plans to go there.

You can try the project here: https://tourism-advisor-app-1005827417526.europe-west4.run.app

The project uses:
1. Google Gemini 2.0 Flash as its LLM
2. LangChain
3. OpenCage Geocoding API for retrieving location coordinates
4. tomorrow.io API for retrieving weather information for that location
5. FourSquare places API for retrieving points of interest near the location
6. Docker
7. Deployed on Google Cloud

# TODO
- Improvement to the UI
- Track LLM with MLFlow
- Add support for Arabic language
- Improvement to recommendations (advise for or against the destination instead of recommending every destination)
- Enrich information retrieved from the APIs (ticket price data, etc.)
- Retrieve images for the destination