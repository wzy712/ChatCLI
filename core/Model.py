from openai.types.chat import ChatCompletion, ChatCompletionMessage

from ChatCLI_types.types import ChatConfig
from openai import OpenAI


def get_response(client: OpenAI, request_body):
    return client.chat.completions.create(model=request_body["model"],
                                          messages=request_body["message"],
                                          tools=request_body["tools"])


class Model:
    def __init__(self, config: ChatConfig, system_prompt: str = ""):
        self.base_url = config["base_url"]
        self.model = config["models"]["default"]
        self.api_key = config["api_key"]
        self.default_thinking_mode = config["thinking_mode"]
        self.client = OpenAI(
            api_key=str(self.api_key),
            base_url=str(self.base_url),
        )

    def send(self, messages, tools) -> tuple[ChatCompletion, ChatCompletionMessage]:
        response = get_response(self.client, self.make_request_body(messages, tools))
        return response, response.choices[0].message

    def make_request_body(self, messages, tools):

        model = self.model

        return {
            "model": model,
            "message": messages,
            "tools": tools
        }
