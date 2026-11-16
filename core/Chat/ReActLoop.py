import os
from copy import deepcopy
from typing import List, Optional

from core.Chat.ChatContext import ChatContextManager
from core.config.ChatConfig import ChatConfig
from core.Tool import Tool
from core.Model import Model
import json

react_system_prompt = """You are a TAO agent built on the ReAct architecture. You operate through a five-state state machine and may only use the following TAO methods:
enter, thought, action, observation, finish.

State transition rules:
1. If there is no prior TAO call in the conversation, you must call enter first. enter creates the state machine and moves it into the thought state.
2. When the current state is thought:
   - To continue the task normally, call thought, record your reasoning, and move to the action state.
   - If the task is complete or no further action is needed, call finish, exit TAO, and use the finish message content as the final summary.
3. When the current state is action, you must call action, record the action for this round, and move to the observation state.
4. When the current state is observation, you must call observation, record the action result or environment feedback, and return to the thought state.
5. After finish is called, TAO exits and you must not call any TAO method again.

Calling constraints:
- Call exactly one TAO function at a time. Do not call multiple TAO functions in parallel or return multiple tool calls at once.
- All five TAO functions take no parameters. When calling them, the arguments must be an empty object {}.
- The semantic content for each phase must be written in the content of that assistant message:
  - enter: write the task objective or initialization information.
  - thought: write the current reasoning, judgment, and intended next step.
  - action: write the specific action to perform or the intended external tool call for this round. Include parameters if necessary, but do not write observation results.
  - observation: write the action result, environment feedback, or error information. Do not write the next-step plan.
  - finish: write the final summary. This content will be written into the conversation history and must be usable directly as the final answer.
- Do not advance the state with ordinary assistant text. Do not skip states. Do not fabricate observation results.
- Determine the current state from the most recent TAO call; do not rely on hidden state. The normal loop is:
  enter → thought → action → observation → thought → ... → finish. """

false = False
true = True

enter_description = {
    "type": "function",
    "function": {
        "name": "enter",
        "description": "Initialize the TAO state machine and enter the thought state. Call this only once, before TAO has been entered. Write the task objective or initialization information in the content of the calling message. Takes no parameters and returns no value.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": false
        }
    }
}

thought_description = {
    "type": "function",
    "function": {
        "name": "thought",
        "description": "Record the current reasoning and advance to the action state. Call this only when the current state is thought and the task should continue. Write the current reasoning, judgment, and intended next step in the content of the calling message. If the task is already complete, call finish instead of thought. Takes no parameters and returns no value.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": false
        }
    }
}

action_description = {
    "type": "function",
    "function": {
        "name": "action",
        "description": "Declare the action for this round and advance to the observation state. Call this only when the current state is action. Write the specific action, intended external tool call, or execution step in the content of the calling message; include parameters if necessary, but do not write observation results. Takes no parameters and returns no value.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": false
        }
    }
}

observation_description = {
    "type": "function",
    "function": {
        "name": "observation",
        "description": "Record the action result and return to the thought state. Call this only when the current state is observation. Write the action execution result, environment feedback, or error information in the content of the calling message; do not write the next-step plan. Takes no parameters and returns no value.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": false
        }
    }
}

finish_description ={
    "type": "function",
    "function": {
      "name": "finish",
      "description": "Exit the TAO state and end the loop. Call this only when the current state is thought and the task is complete or no further action is needed. The content of the calling message is the final summary and will be written into the conversation history. Do not call any TAO method after finish. Takes no parameters and returns no value.",
      "parameters": {
        "type": "object",
        "properties": {},
        "required": [],
        "additionalProperties": false
      }
    }
  }

none_func = lambda x: "None"
enter_tool = Tool("enter", description=enter_description, function=none_func)
thought_tool = Tool("thought", description=thought_description, function=none_func)
action_tool = Tool("action", description=action_description, function=none_func)
observation_tool = Tool("observation", description=observation_description, function=none_func)
finish_tool = Tool("finish", description=finish_description, function=lambda x: x)

ReActTool = [enter_tool, thought_tool, action_tool, observation_tool, finish_tool]
react_tool_name = ["enter", "thought", "action", "observation", "finish"]


class ReActLoop:
    tools: List[Tool]
    model: Model

    def __init__(self, config: ChatConfig, model: Model):
        self.model = model
        self.tools = ReActTool
        self.tools.extend(config.tools)

    def run(self, chat_name: Optional[str] = None):
        if chat_name is None:
            import time
            chat_name = f"new_chat_{time.time()}"
        with ChatContextManager(chat_name) as chat_context:
            messages = chat_context.messages
            if len(messages) == 0:
                messages.append({"role": "system", "content": react_system_prompt})

            model = self.model
            tools = [tool.description for tool in self.tools]
            functions = {tool.name: tool.function for tool in self.tools}
            TAO_history = []

            while True:
                user_input = input("User>\t")

                if user_input == "###quit":
                    break

                messages.append({"role": "user", "content": user_input})

                response, message = model.send(messages, tools)
                print(f"Assistant>\t{message.content}")
                is_in_tao = False

                while response.choices[0].finish_reason == "tool_calls":
                    tool_calls = message.tool_calls

                    if tool_calls is None:
                        break

                    tool_names = [tool.function.name for tool in tool_calls]
                    if "enter" in tool_names:
                        is_in_tao = True

                    is_finish="finish" in tool_names
                    if is_finish:
                        is_in_tao = False
                        TAO_history=[]

                    if is_in_tao:
                        TAO_history.append(message)

                    if is_finish:
                        result=json.loads(tool_calls[0].function.arguments)["content"]
                        message = {"role": "assistant", "content": result}
                        print(f"Assistant>\t{result}")
                        break
                    for tool in tool_calls:
                        name = tool.function.name
                        arg = json.loads(tool.function.arguments)

                        if is_in_tao:
                            TAO_history.append(
                            {"role": "tool", "tool_call_id": tool.id, "content": "None" if name in react_tool_name else functions[name](arg)})
                        else:
                            messages.append(
                            {"role": "tool", "tool_call_id": tool.id, "content": functions[name](arg)})
                        print(f"Tool call>\t{tool.function.name}\t{arg}")
                    response, message = model.send(messages + TAO_history, tools)
                    print(message.content)
                messages.append(message)
