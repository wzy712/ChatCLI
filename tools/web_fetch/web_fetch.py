from ChatCLI_main import api_key

def web_fetch(arg):
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

