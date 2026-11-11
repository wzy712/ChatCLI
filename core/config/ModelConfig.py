import json
from typing import Optional


class ModelConfig:
    def __init__(self, source_path: Optional[str] = None, data=None):
        if source_path:
            with open(source_path, "r", encoding="utf-8") as file:
                self.data = json.load(file)
                data = self.data

        self.base_url = data["base_url"]
        self.api_key = data["api_key"]
        self.model_name = data["model_name"]

    def __getitem__(self, item):
        return self.data[item]
