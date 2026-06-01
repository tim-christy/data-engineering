import os
from datetime import datetime

from dotenv import load_dotenv
from airflow.sdk import dag
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.operators.bash import BashOperator

from pathlib import Path
load_dotenv(Path(__file__).parent / ".env-api")

import logging
logging.getLogger(__name__).info(f"IMAGE_NAME={os.environ.get('IMAGE_NAME')}")
logging.getLogger(__name__).info(f"DOCKER_NETWORK={os.environ.get('DOCKER_NETWORK')}")

@dag(
  start_date=datetime(2024, 1, 1),
  schedule="@daily",
  catchup=False,
)
def api_ingest():

  noaa_ingestion = DockerOperator(
      task_id="noaa_ingestion",
      image=os.environ.get("IMAGE_NAME"),
      network_mode=os.environ.get("DOCKER_NETWORK"),
      mount_tmp_dir=False,
      environment={
          "ECS_USER": os.environ.get("ECS_USER"),
          "POSTGRES_DB": os.environ.get("POSTGRES_DB"),
          "ECS_PASSWORD": os.environ.get("ECS_PASSWORD"),
          "POSTGRES_HOST": os.environ.get("POSTGRES_HOST"),
          "POSTGRES_PORT": os.environ.get("POSTGRES_PORT"),
          "NOAA_SCHEMA_DESTINATION": os.environ.get("NOAA_SCHEMA_DESTINATION"),
          "NOAA_TABLE_DESTINATION": os.environ.get("NOAA_TABLE_DESTINATION"),
          "LOGGING_SCHEMA": os.environ.get("LOGGING_SCHEMA"),
          "LOGGING_TABLE": os.environ.get("LOGGING_TABLE")
      },
  )

  test = BashOperator(
      task_id="test",
      bash_command=f"echo 'test'"
  )


  dag = test >> noaa_ingestion

api_ingest()


