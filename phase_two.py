from dataclasses import dataclass
from typing import List, Dict, Optional
import os
import requests
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Position:
    row: int
    column: int

    def to_dict(self) -> Dict:
        return {"row": self.row, "column": self.column}


class AstralObject:
    def __init__(self, position: Position):
        self.position = position

    def to_api_params(self) -> Dict:
        return self.position.to_dict()


class Soloon(AstralObject):
    def __init__(self, position: Position, color: str):
        super().__init__(position)
        self.color = color

    def to_api_params(self) -> Dict:
        params = super().to_api_params()
        params["color"] = self.color
        return params


class Cometh(AstralObject):
    def __init__(self, position: Position, direction: str):
        super().__init__(position)
        self.direction = direction

    def to_api_params(self) -> Dict:
        params = super().to_api_params()
        params["direction"] = self.direction
        return params


class Polyanet(AstralObject):
    pass


class MegaverseAPI:
    def __init__(self, base_url: str, candidate_id: str):
        self.base_url = base_url.rstrip("/")
        self.candidate_id = candidate_id
        self.session = requests.Session()

    def _make_request(
        self,
        endpoint: str,
        method: str,
        data: Dict,
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ) -> Optional[requests.Response]:
        """Make an API request with retry logic."""
        url = f"{self.base_url}{endpoint}"
        data["candidateId"] = self.candidate_id

        for attempt in range(max_retries):
            try:
                response = self.session.request(
                    method=method, url=url, json=data, timeout=10
                )
                response.raise_for_status()
                return response
            except requests.exceptions.RequestException as e:
                logger.warning(
                    f"Request failed (attempt {attempt + 1}/{max_retries}): {str(e)}"
                )
                if attempt < max_retries - 1:
                    sleep_time = retry_delay * (2**attempt)
                    time.sleep(sleep_time)
                continue

        return None

    def create_object(self, obj: AstralObject) -> bool:
        endpoint_map = {
            "Polyanet": "/polyanets",
            "Soloon": "/soloons",
            "Cometh": "/comeths",
        }
        endpoint = endpoint_map[obj.__class__.__name__]
        response = self._make_request(
            endpoint=endpoint, method="POST", data=obj.to_api_params()
        )
        return response is not None

    def get_goal_map(self) -> List[List[str]]:
        """Fetch the goal map for the candidate."""
        endpoint = f"/map/{self.candidate_id}/goal"
        response = self._make_request(endpoint=endpoint, method="GET")
        if response and response.status_code == 200:
            return response.json().get("goal", [])
        else:
            logger.error("Failed to retrieve goal map.")
            return []


class MegaverseCreator:
    def __init__(self, api: MegaverseAPI):
        self.api = api

    def parse_goal_map(self, goal_map: List[List[str]]) -> List[AstralObject]:
        """Parse goal map and return a list of AstralObjects with the correct attributes."""
        objects = []
        for row_index, row in enumerate(goal_map):
            for col_index, cell in enumerate(row):
                position = Position(row=row_index, column=col_index)

                if cell == "POLYANET":
                    objects.append(Polyanet(position))
                elif cell.endswith("SOLOON"):
                    color = cell.split("_")[0].lower()  # Extract color
                    objects.append(Soloon(position, color=color))
                elif cell.endswith("COMETH"):
                    direction = cell.split("_")[0].lower()  # Extract direction
                    objects.append(Cometh(position, direction=direction))
        return objects

    def create_megaverse(self) -> None:
        """Main method to create the megaverse based on the goal map."""
        goal_map = self.api.get_goal_map()
        if not goal_map:
            logger.error("Goal map retrieval failed, cannot proceed.")
            return

        objects = self.parse_goal_map(goal_map)
        for obj in objects:
            if self.api.create_object(obj):
                logger.info(f"Created {obj.__class__.__name__} at {obj.position}")
            else:
                logger.error(
                    f"Failed to create {obj.__class__.__name__} at {obj.position}"
                )
            time.sleep(0.5)  # Delay to avoid rate limits


def main():
    # Configuration using environment variables
    API_BASE_URL = os.getenv("API_BASE_URL", "https://challenge.crossmint.io/api")
    CANDIDATE_ID = os.getenv("CANDIDATE_ID")

    if not CANDIDATE_ID:
        logger.error("CANDIDATE_ID environment variable not set.")
        return

    # Initialize API and Megaverse Creator
    api = MegaverseAPI(API_BASE_URL, CANDIDATE_ID)
    creator = MegaverseCreator(api)

    # Create Crossmint logo pattern
    logger.info("Starting Crossmint logo creation...")
    creator.create_megaverse()
    logger.info("Crossmint logo creation completed!")


if __name__ == "__main__":
    main()
