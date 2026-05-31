from pathlib import Path

import yaml

coordinates_path = Path(__file__).parent/"coordinates.yml"

# Read in coordinates.yml and convert lat/long to strings
with open(coordinates_path, "r") as f:
    coordinates = yaml.safe_load(f)

class Config:
    """Handles the postgres database connection and coordinate configs"""
    def __init__(self):
        self.coordinates = coordinates

    def get_coordinates(self, city: str) -> dict[str, str]:
        if self.coordinates.get(city) is None:
            raise KeyError(
                f"Coordinates for {city} have not been set."
            )
        return self.coordinates.get(city)
