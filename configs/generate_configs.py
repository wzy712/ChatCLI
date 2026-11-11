from collections.abc import Callable
from typing import Tuple, List, Union

from core.config.ChatConfig import ChatConfig
from core.config.ModelConfig import ModelConfig

import os
from pathlib import Path

from core.Tool import Tool

root_path=Path("..")

api_providers = ["DeepSeek"]
base_urls = {"DeepSeek": "https://api.deepseek.com"}
models = {"DeepSeek": {"flash": "deepseek-flash"}}
tool_paths = {"default": "./tools"}
tools = ["web_search", "fetch_webpage"]
api_key = {"DeepSeek": ["sk-d64d3a41b11a4d92860ebd8793d75bbb"]}

def import_tool_function(tool_folder: Union[str, Path]) -> List[Tool]:
    pass

def make_tools()->List[Callable]:
    #default include ./tools
    tool_folders = os.listdir(root_path/tool_paths["default"][0])
    tools=[]
    for tool_folder in tool_folders:
        tools.extend()
    return tools


def default_chat_model_config() -> Tuple[ChatConfig, ModelConfig]:
    chat_config=ChatConfig({"tools": make_tools()})