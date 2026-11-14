from pathlib import Path

from core.config.ChatConfig import ChatConfig
from core.config.ModelConfig import ModelConfig
from core.ChatLoop import ChatLoop
from core.Model import Model
from core.loader.ToolLoader import load_tool

api_key = "sk-fd893ccb5d024555970c2b7874fc435f"  # 改成你自己的deepseek apikey


def get_weather(arg):
    return "24摄氏度"


def web_search(arg):
    query = arg["query"]
    count = arg["count"]
    import requests

    response = requests.post(
        "https://api.deepseek.com/v1/tools/search",
        headers={
            "Authorization": f"Bearer {api_key}",
        },
        json={
            "query": query,
            "count": count,
            "need_content": True,
        },
    )
    response.raise_for_status()
    results = [{"type": "text", "text": f"title: {result["title"]}\nurl: {result["url"]}\nsummary: {result["summary"]}"}
               for result in response.json()["results"]]
    return results


def fetch_webpage(arg):
    import requests
    url = arg["url"]

    response = requests.post(
        "https://api.deepseek.com/v1/tools/fetch",
        headers={
            "Authorization": f"Bearer {api_key}",
        },
        json={"url": url},
    )
    response.raise_for_status()
    page = response.json()
    return [{"type": "text", "text": f"title: {page["title"]}\ncontent: {page["content"]}"}]


def main():
    tools = [
        load_tool(Path("tools/web_search"), "web_search"),
        load_tool(Path("tools/web_fetch"), "web_fetch")
    ]
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

