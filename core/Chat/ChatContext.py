import os
import pickle
from contextlib import contextmanager
from pathlib import Path
from typing import List, Dict, Optional

chat_memory_folder: Path = Path("chat_memory")


@contextmanager
def ChatContextManager(chat_name: str):
    chat_file: str = f"{chat_name}.pickle"
    if not os.path.exists(chat_memory_folder):
        os.mkdir(chat_memory_folder)
    chat_list = os.listdir(chat_memory_folder)
    context: ChatContext = ChatContext()
    file_path = chat_memory_folder / chat_file
    try:
        if chat_file in chat_list:
            # open exist
            context = deserialize_chat_context(file_path)

        yield context

    finally:
        serialize_chat_context(context, file_path)


def deserialize_chat_context(file_path: Path) -> ChatContext:
    with open(file_path, 'rb') as file:
        context = pickle.load(file)

    return context


def serialize_chat_context(context: ChatContext, file_path: Path) -> None:
    with open(file_path, 'wb',) as file:
        pickle.dump(context, file)


class ChatContext:
    messages: List[Dict[str, str]]

    def __init__(self, messages: Optional[List[Dict[str, str]]] = None):
        if messages is not None:
            self.messages = messages
        else:
            self.messages = []
