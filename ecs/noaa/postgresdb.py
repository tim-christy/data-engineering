import os
from psycopg import connect, sql
from psycopg.types.json import Jsonb

# Postgres
class Postgressor:
    """Handles all raw data/database interactions"""
    def __init__(self):
        self.conn_string = (
          f"postgresql://{os.getenv('ECS_USER')}:{os.getenv('ECS_PASSWORD')}"
          f"@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}"
          f"/{os.getenv('POSTGRES_DB')}"
        )
        self.conn = connect(self.conn_string)

    def create_raw_noaa_table_if_not_exists(self):
        with self.conn.cursor() as cursor:
            cursor.execute(
                sql.SQL( """CREATE SCHEMA IF NOT EXISTS {};"""
                ).format(
                    sql.Identifier(os.environ["NOAA_SCHEMA_DESTINATION"])
                )
            )
            cursor.execute(
                sql.SQL(
                """
                    CREATE TABLE IF NOT EXISTS {}.{} (
                        id UUID DEFAULT gen_random_uuid(),
                        data JSONB,
                        source TEXT,
                        ingested_at TIMESTAMPTZ DEFAULT NOW()
                    );
                """
                ).format(
                    sql.Identifier(os.environ["NOAA_SCHEMA_DESTINATION"]),
                    sql.Identifier(os.environ["NOAA_TABLE_DESTINATION"]),
                )
            )

    def insert_noaa_data(self, data, source):
        with self.conn.cursor() as cursor:
            cursor.execute(
                sql.SQL(
                    "INSERT INTO {}.{}(data, source) VALUES (%s, %s)"
                ).format(
                    sql.Identifier(os.environ["NOAA_SCHEMA_DESTINATION"]),
                    sql.Identifier(os.environ["NOAA_TABLE_DESTINATION"])
                ),
                (Jsonb(data), source)
            )
