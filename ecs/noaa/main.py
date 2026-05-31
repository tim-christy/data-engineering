import logging
import os

from pathlib import Path

from dotenv import load_dotenv

from config import Config
from weather import WeatherData
from postgresdb import Postgressor

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(name=__name__)

# Credentials
env_path = Path(__file__).parent/".env"
load_dotenv(env_path)


def main():

    config = Config()
    postgres = Postgressor()
    postgres.create_raw_noaa_table_if_not_exists()

    # Get coordinates
    logger.info("Preparing coordinates")
    weather_objs = [ 
        WeatherData(k, v["lat"], v["long"]) 
        for k, v in config.coordinates.items()
    ]

    logger.info("Getting forecast data from noaa api")
    # Get forecast data
    for weather in weather_objs:
        logger.info(f"Getting data for {weather.location}")
        weather.get_grid_data()
        weather.get_forecast()
        weather.get_hourly_forecast()
        logger.info("Success")
        logger.info("Logging data into raw")
        postgres.insert_noaa_data(weather.grid_data, "grid_data")
        postgres.insert_noaa_data(weather.forecast_data, "forecast_data")
        postgres.insert_noaa_data(
            weather.forecast_hourly_data, "forecast_hourly_data")
        logger.info("Success")

    logger.info("Run complete, app ran successfully")

    postgres.conn.commit()


if __name__ == "__main__":
    main()
