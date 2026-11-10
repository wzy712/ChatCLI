from core.Model import Model
import json

api_key="sk-xxxxxxxxxxxxxxxxxxxxxxx" #改成你自己的deepseek apikey

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
        {
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
        },
        {
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
        },
        {
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
        }
    ]
    tool_function_map = {"get_weather": get_weather,
                         "web_search": web_search,
                         "fetch_webpage": fetch_webpage}

    messages = []
    model = Model({
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
        "api_key": f"{api_key}"
    })

    while True:
        user_input = input("User>\t")
        messages.append({"role": "user", "content": user_input})
        response, message = model.send(messages, tools)
        print(f"Assistant>\t{message.content}")

        while response.choices[0].finish_reason == "tool_calls":
            messages.append(message)
            for tool in message.tool_calls:
                name = tool.function.name
                arg = json.loads(tool.function.arguments)

                messages.append({"role": "tool", "tool_call_id": tool.id, "content": tool_function_map[name](arg)})
                print(f"Tool call>\t{tool.function.name}\t{arg}")
            response, message = model.send(messages, tools)
            print(message.content)
        messages.append(message)


if __name__ == "__main__":
    main()

"""
上网搜索，世界上最好玩的国产二字二次元开放大世界是哪款，只能说一个答案，不准端水
"""
