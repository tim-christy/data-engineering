"""
Config holds all the configuration variables and other constants like urls for
the api endpoints
"""
import os
import pathlib
from dotenv import load_dotenv

import requests

dotenv_path = pathlib.Path(__file__).parent / ".env-api"
if not load_dotenv(dotenv_path):
    raise FileNotFoundError("Missing .env-api")

class NOAAConfig:
    def __init__(self):
        self.url_noaa = os.environ["NOAA_BASE_URL"].strip().strip("/")
        self.latitude = None
        self.longitude = None

    def set_coordinates(self, city):
        if city.strip().lower() == "bay ridge":
            self.latitude = os.environ["LATITUDE_BAY_RIDGE"]
            self.longitude = os.environ["LONGITUDE_BAY_RIDGE"]
            self.points_endpoint = (
                f"{self.url_noaa}/points/{self.latitude},{self.longitude}"
            )
            headers = {
                "User-Agent": "(timsdatapipeline, tim@timchristy.io)"
            }
            response = requests.get(self.points_endpoint, headers=headers)
            response.raise_for_status()
            links = response.json()
            self.forecast = links["properties"]["forecast"]
            self.hourly_forecast = links["properties"]["forecastHourly"]


