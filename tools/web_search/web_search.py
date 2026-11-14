from ChatCLI_main import api_key

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
