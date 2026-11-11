from typing import List

from core.config.ChatConfig import ChatConfig
from core.Tool import Tool
from core.Model import Model
import json


class ChatLoop:
    tools: List[Tool]
    model: Model

    def __init__(self, config: ChatConfig, model: Model):
        self.messages = []
        self.model = model
        self.tools = config.tools

    def run(self):
        messages = self.messages
        model = self.model
        tools = [tool.description for tool in self.tools]
        functions = {tool.name: tool.function for tool in self.tools}

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

                    messages.append({"role": "tool", "tool_call_id": tool.id, "content": functions[name](arg)})
                    print(f"Tool call>\t{tool.function.name}\t{arg}")
                response, message = model.send(messages, tools)
                print(message.content)
            messages.append(message)
