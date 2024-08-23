import json
from typing import Dict, Any


class DataManager:

    @staticmethod
    def save_data_to_cache(filename: str, data: Dict[str, Any]) -> None:
        with open(filename, 'w') as cache:
            json.dump(data, cache, indent=4)

    @staticmethod
    def load_data_from_cache(filename: str) -> Dict[str, Any]:
        with open(filename, 'r') as cache:
            cached_file = json.load(cache)
        return cached_file
