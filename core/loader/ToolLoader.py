import os
from pathlib import Path

import json

import sys
from typing import List

from core.Tool import Tool
import importlib.util as ipu


def load_tool(folder_path: Path, tool_name: str) -> Tool:
    with open(folder_path / f"{tool_name}.json", "r", encoding="utf-8") as file:
        description = json.load(file)

    func_name = description["function"]["name"]
    module_name = func_name
    spec = ipu.spec_from_file_location(module_name, str(folder_path / f"{func_name}.py"))

    if spec is None:
        raise ImportError(f"load_tool: 无法从{folder_path}导入工具")

    module = ipu.module_from_spec(spec)
    sys.modules[module_name]=module
    spec.loader.exec_module(module)

    func = getattr(module, func_name)
    return Tool(func_name, description, func)

class ToolLoader:
    def __call__(self, source_path: Path, tool_list: List[str]):
        folders=os.listdir(source_path)
        tools=[]
        for tool in tool_list:
            tools.append(load_tool(Path(source_path)/tool, tool))

        return tools

