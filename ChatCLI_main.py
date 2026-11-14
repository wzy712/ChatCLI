from pathlib import Path

from core.config.ChatConfig import ChatConfig
from core.config.ModelConfig import ModelConfig
from core.ChatLoop import ChatLoop
from core.Model import Model
from core.loader.ToolLoader import ToolLoader

api_key = "sk-xxxxxxxxxxxxxxxxx"  # 改成你自己的deepseek apikey


def main():
    tool_loader=ToolLoader()
    tools = tool_loader(Path("tools"), ["web_search", "web_fetch"])
    messages = []
    config = {
        "base_url": "https://api.deepseek.com",
        "models": {
            "default": "deepseek-flash"
        },
        "protocol_type": "OpenAI",
        "thinking_mode": {
            "thinking": "disabled",
            "reasoning_effort": "low"
        },
        "tool_path": "./tools",
        "tools": tools,
        "api_key": f"{api_key}",
    }
    chat_config = ChatConfig(data={"tools": tools})
    model_config = ModelConfig(data={"base_url": "https://api.deepseek.com",
                                     "api_key": api_key,
                                     "model_name": "deepseek-flash"})
    model = Model(model_config)
    main = ChatLoop(chat_config, model)
    main.run()


if __name__ == "__main__":
    main()

