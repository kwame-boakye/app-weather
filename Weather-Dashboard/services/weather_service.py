import requests
from utils.logger import logger
from config.constants import BASE_URL, FORECAST_URL


class WeatherService:
    def __init__(self, api_key):
        self.api_key = api_key
        self.session = requests.Session()

    def get_current_weather(self, location):
        """Fetch current weather data"""
        try:
            logger.info(f"Fetching weather data for location: {location}")
            params = {"appid": self.api_key, "q": location}
            response = self.session.get(BASE_URL, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching weather: {str(e)}")
            raise

    def get_forecast(self, location):
        """Fetch forecast data"""
        try:
            logger.info(f"Fetching forecast for location: {location}")
            params = {"appid": self.api_key, "q": location}
            response = self.session.get(FORECAST_URL, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching forecast: {str(e)}")
            raise
