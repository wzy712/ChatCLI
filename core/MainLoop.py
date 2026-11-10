from typing import Dict, Union, List

from core.Model import Model
import json

from ChatCLI_types.types import ChatConfig


class MainLoop:
    def __init__(self, config: ChatConfig):
        self.messages=[]
        self.model=Model(config)
        self.tools=config["tools"]
        self.tool_function_map=config["tool_function_map"]

    def run(self):
        messages=self.messages
        model=self.model
        tools=self.tools
        tool_function_map=self.tool_function_map

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