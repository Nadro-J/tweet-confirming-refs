import os
import json
from typing import Dict, Any


class DataManager:

    @staticmethod
    def save_data_to_cache(filename: str, data: Dict[str, Any]) -> None:
        with open(filename, 'w') as cache:
            json.dump(data, cache, indent=4)

    @staticmethod
    def load_data_from_cache(filename: str) -> Dict[str, Any]:
        # Check if the file exists
        if not os.path.exists(filename):
            # If the file doesn't exist, create it with an empty dictionary
            with open(filename, 'w') as cache:
                json.dump({}, cache)

        # Now, load the file content
        with open(filename, 'r') as cache:
            cached_file = json.load(cache)

        return cached_file
