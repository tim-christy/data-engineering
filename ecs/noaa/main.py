import logging
import os

from pathlib import Path

import psycopg
import requests

from dotenv import load_dotenv
from psycopg import sql
from psycopg.types.json import Jsonb


# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(name=__name__)

# Credentials
env_path = Path(__file__).parent/".env"
certificate_path = str(Path("~/cloudflare-ca.pem").expanduser())
load_dotenv(env_path)

# Postgres
conn_string = (
  f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}"
  f"@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}"
  f"/{os.getenv('POSTGRES_DB')}"
)
conn = psycopg.connect(conn_string)

def insert_noaa_data(data, source):
    with conn.cursor() as cursor:
        logger.info(f"Inserting {source}")
        cursor.execute(
            sql.SQL(
                "INSERT INTO {}.{}(data, source) VALUES (%s, %s)"
            ).format(
                sql.Identifier(os.environ["POSTGRES_SCHEMA"]),
                sql.Identifier(os.environ["POSTGRES_TABLE"])
            ),
            (Jsonb(data), source)
        )
        logger.info("Success")



def main():

    # Get grid data - converts lat/long to whatever standard noaa uses
    logger.info("Getting grid data")
    grid_url = (
        f'https://api.weather.gov/points/{os.environ["BAY_RIDGE_LAT"]},'
        f'{os.environ["BAY_RIDGE_LONG"]}'
    )
    response = requests.get(grid_url, verify=certificate_path)
    response.raise_for_status()
    grid_data = response.json()
    logger.info("Grid data received successfully")

    # Take properties key from grid data to get forecast endpoints
    # forecast
    logger.info("Getting forecast data")
    properties = grid_data["properties"]
    forecast_url = properties["forecast"]
    forecast_response = requests.get(forecast_url, verify=certificate_path)
    forecast_response.raise_for_status()
    forecast_data = forecast_response.json()
    logger.info("Forecast data received successfully")

    # forecast hourly
    logger.info("Getting hourly forecast data")
    forecast_hourly_url = properties["forecastHourly"]
    forecast_hourly_response = requests.get(forecast_hourly_url,
                                            verify=certificate_path)
    forecast_hourly_response.raise_for_status()
    forecast_hourly_data = forecast_hourly_response.json()
    logger.info("Hourly forecast data received successfully")

    # Insert data into DB
    logger.info(
        f"Creating {os.environ["POSTGRES_DB"]}"
        f".{os.environ["POSTGRES_SCHEMA"]}"
        f".{os.environ["POSTGRES_TABLE"]}"
        " if it does not exist"
    )
    with conn.cursor() as cursor:
        cursor.execute(
            sql.SQL(
            """
                CREATE SCHEMA IF NOT EXISTS {};
                CREATE TABLE IF NOT EXISTS {}.{} (
                    id UUID DEFAULT gen_random_uuid(),
                    data JSONB,
                    source TEXT,
                    ingested_at TIMESTAMPTZ DEFAULT NOW()
                );
            """
            ).format(
                sql.Identifier(os.environ["POSTGRES_SCHEMA"]),
                sql.Identifier(os.environ["POSTGRES_SCHEMA"]),
                sql.Identifier(os.environ["POSTGRES_TABLE"]),
            )
        )

    insert_noaa_data(grid_data, "grid_data")
    insert_noaa_data(forecast_data, "forecast_data")
    insert_noaa_data(forecast_hourly_data, "forecast_hourly_data")
    conn.commit()
    conn.close()



if __name__ == "__main__":
    main()
