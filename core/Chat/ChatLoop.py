import os
from typing import List, Optional

from core.Chat.ChatContext import ChatContextManager
from core.config.ChatConfig import ChatConfig
from core.Tool import Tool
from core.Model import Model
import json


class ChatLoop:
    tools: List[Tool]
    model: Model

    def __init__(self, config: ChatConfig, model: Model):
        self.model = model
        self.tools = config.tools

    def run(self, chat_name: Optional[str] = None):
        if chat_name is None:
            from core.Chat.ChatContext import chat_memory_folder
            num_chat = len(os.listdir(chat_memory_folder))
            chat_name=f"new_chat_{num_chat}"
        with ChatContextManager(chat_name) as chat_context:
            messages = chat_context.messages
            model = self.model
            tools = [tool.description for tool in self.tools]
            functions = {tool.name: tool.function for tool in self.tools}

            while True:
                user_input = input("User>\t")

                if user_input == "###quit":
                    break

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
