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


class Polyanet(AstralObject):
    pass


class MegaverseAPI:
    def __init__(self, base_url: str, candidate_id: str):
        """Initialize the Megaverse API client."""
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
    ) -> bool:
        """Make an API request with retry logic."""
        url = f"{self.base_url}{endpoint}"
        data["candidateId"] = self.candidate_id

        for attempt in range(max_retries):
            try:
                response = self.session.request(
                    method=method, url=url, json=data, timeout=10
                )
                response.raise_for_status()
                return True
            except requests.exceptions.RequestException as e:
                logger.warning(
                    f"Request failed (attempt {attempt + 1}/{max_retries}): {str(e)}"
                )
                if attempt < max_retries - 1:
                    sleep_time = retry_delay * (2**attempt)
                    time.sleep(sleep_time)
                continue

        return False

    def create_polyanet(self, position: Position) -> bool:
        """Create a Polyanet at the specified position."""
        return self._make_request(
            endpoint="/polyanets", method="POST", data=position.to_dict()
        )

    def delete_polyanet(self, position: Position) -> bool:
        """Delete a Polyanet at the specified position."""
        return self._make_request(
            endpoint="/polyanets", method="DELETE", data=position.to_dict()
        )


class MegaverseCreator:
    def __init__(self, api: MegaverseAPI, grid_size: int):
        """Initialize the Megaverse Creator."""
        self.api = api
        self.grid_size = grid_size

    def _is_valid_position(self, position: Position) -> bool:
        """Check if a position is valid within the grid."""
        return (
            0 <= position.row < self.grid_size and 0 <= position.column < self.grid_size
        )

    def _generate_x_shape_positions(self) -> List[Position]:
        """Generate positions for X-shape pattern."""
        positions = []

        # Create X pattern
        for i in range(2, 9):  # From index 2 to 8 (inclusive)
            # Main diagonal
            positions.append(Position(row=i, column=i))
            # Counter diagonal
            positions.append(Position(row=i, column=self.grid_size - 1 - i))

        return positions

    def create_x_shape(self) -> None:
        """Create an X shape pattern of Polyanets."""
        positions = self._generate_x_shape_positions()

        for position in positions:
            if not self._is_valid_position(position):
                logger.warning(f"Skipping invalid position: {position}")
                continue

            if self.api.create_polyanet(position):
                logger.info(f"Successfully created Polyanet at position {position}")
            else:
                logger.error(f"Failed to create Polyanet at position {position}")

            # Add delay between requests to avoid rate limiting
            time.sleep(0.5)


def main():
    """Main function to run the Megaverse creator."""
    # Load configuration from environment variables
    API_BASE_URL = os.getenv("API_BASE_URL", "https://challenge.crossmint.io/api")
    CANDIDATE_ID = os.getenv("CANDIDATE_ID")
    GRID_SIZE = 11

    if not CANDIDATE_ID:
        logger.error("CANDIDATE_ID environment variable not set.")
        return

    try:
        # Initialize API and creator
        api = MegaverseAPI(API_BASE_URL, CANDIDATE_ID)
        creator = MegaverseCreator(api, GRID_SIZE)

        # Create X shape
        logger.info("Starting X-shape creation...")
        creator.create_x_shape()
        logger.info("X-shape creation completed!")

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()
