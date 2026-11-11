from core.config.ChatConfig import ChatConfig
from core.config.ModelConfig import ModelConfig
from core.ChatLoop import ChatLoop
from core.Model import Model
from core.Tool import Tool

api_key = "sk-d64d3a41b11a4d92860ebd8793d75bbb"  # 改成你自己的deepseek apikey


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
        Tool("get_weather", {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get weather of a location, the user should supply a location first.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city and state, e.g. San Francisco, CA",
                        },
                    },
                    "required": ["location"],
                },
            },
        }, get_weather),
        Tool("web_search", {
            "type": "function",
            "function": {
                "name": "web_search",
                "description": "Search the web by query and get structured results.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": """Search terms, 1 to 128 Unicode characters, can't be all blank, supports the search syntax listed below.
                            Search Syntax

The search syntax in the query is passed directly to the search service. The examples in the table below combine operators with search terms; you can combine multiple operators in one query.

Operator Example Description
site: DeepSeek site:github.com Limits results to a specified site, for multiple sites separate with spaces and connect using OR, e.g., DeepSeek site:github.com OR site:huggingface.co.
-site: DeepSeek -site:example.com Exclude specified sites, for multiple sites separate with spaces.
- DeepSeek -ads Exclude pages containing specified keywords, separate multiple keywords with spaces.
-"..." DeepSeek -"release notes" Exclude pages containing specified phrases, phrases can contain spaces, separate multiple phrases with spaces.
"..." DeepSeek "exact phrase" Exact match for specified phrases, separate multiple phrases with spaces.
lang: DeepSeek lang:zh,en Limit results to specified languages, separate multiple languages with commas, e.g., lang:zh,en.
after: DeepSeek after:2025 or DeepSeek after:2025-01-01 Limit results to pages published after the specified date.
before: DeepSeek before:2026 or DeepSeek before:2026-06-01 Limit results to pages published before the specified date.
For example:

{
"query": "DeepSeek model site:github.com OR site:huggingface.co lang:zh after:2025",
"count": 10
}"""
                        },
                        "count": {
                            "type": "integer",
                            "description": "Number of returns, 1 to 50."
                        }
                    },
                    "required": ["query", "count"]
                }
            }
        }, web_search),
        Tool("fetch_webpage", {
            "type": "function",
            "function": {
                "name": "fetch_webpage",
                "description": "Grab a single webpage and return the page content as Markdown text.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "The web address to grab should be no longer than 8192 characters, must be an HTTP/HTTPS URL with a host, and cannot contain a username or password."
                        }
                    }
                },
                "required": ["url"]
            }
        }, fetch_webpage)
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

"""
上网搜索，世界上最好玩的国产二字二次元开放大世界是哪款，只能说一个答案，不准端水
"""
