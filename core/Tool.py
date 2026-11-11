from collections.abc import Callable
from typing import Dict, List


class Tool:
    name: str
    description: Dict[str, Dict | List | str]
    function: Callable

    def __init__(self, name: str, description: Dict[str, Dict | List | str], function: Callable):
        self.name = name
        self.description = description
        self.function = function
