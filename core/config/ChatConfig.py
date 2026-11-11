import json
from typing import Optional, List

from core.Tool import Tool


class ChatConfig:
    tools: List[Tool]
    def __init__(self, source_path: Optional[str] = None, data=None):
        if source_path:
            with open(source_path, 'r', encoding='utf-8') as file:
                self.data = json.load(file)
                data = self.data

        self.tools = data["tools"]


    def __getitem__(self, item):
        return self.data[item]