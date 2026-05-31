import requests
from dataclasses import dataclass

NOAA_BASE_URL = "https://api.weather.gov/points"

@dataclass
class WeatherData:
    location: str
    lat: float
    long: float

    def get_grid_url(self):
        return f"{NOAA_BASE_URL}/{str(self.lat)},{str(self.long)}"
    
    def get_grid_data(self):
        grid_url = self.get_grid_url()
        response = requests.get(grid_url)
        response.raise_for_status()
        self.grid_data = response.json()

    def get_forecast(self):
        if self.grid_data is None:
            self.get_grid_data()
        forecast_url = self.grid_data["properties"]["forecast"]
        forecast_response = requests.get(forecast_url)
        forecast_response.raise_for_status()
        self.forecast_data = forecast_response.json()

    def get_hourly_forecast(self):
        if self.grid_data is None:
            self.get_grid_data()
        forecast_hourly_url = self.grid_data["properties"]["forecastHourly"]
        forecast_hourly_response = requests.get(forecast_hourly_url)
        forecast_hourly_response.raise_for_status()
        self.forecast_hourly_data = forecast_hourly_response.json()

