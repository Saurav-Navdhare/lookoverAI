import json
from typing import Sequence

from langchain.chat_models import ChatOpenAI
from langchain.memory import ChatMessageHistory
from llama_index.tools import BaseTool, FunctionTool

import psycopg2
from dotenv import load_dotenv
import openai
import os

# load the environment variables
load_dotenv()
DB_URI=os.getenv("DB_URI")
openai.api_key=os.getenv("OPENAI_API_KEY")

conn = psycopg2.connect(DB_URI)
cur = conn.cursor()


class YourOpenAIAgent:
    def __init__(
        self,
        tools: Sequence[BaseTool] = [],
        llm: ChatOpenAI = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo-0613"),
        chat_history: ChatMessageHistory = ChatMessageHistory(),
    ) -> None:
        self._llm = llm
        self._tools = {tool.metadata.name: tool for tool in tools}
        self._chat_history = chat_history

    def reset(self) -> None:
        self._chat_history.clear()

    def chat(self, message: str) -> str:
        chat_history = self._chat_history
        chat_history.add_user_message(message)
        functions = [tool.metadata.to_openai_function() for _, tool in self._tools.items()]

        ai_message = self._llm.predict_messages(chat_history.messages, functions=functions)
        chat_history.add_message(ai_message)

        function_call = ai_message.additional_kwargs.get("function_call", None)
        if function_call is not None:
            function_message = self._call_function(function_call)
            chat_history.add_message(function_message)
            ai_message = self._llm.predict_messages(chat_history.messages)
            chat_history.add_message(ai_message)

        return ai_message.content

    def _call_function(self, function_call: dict) -> FunctionMessage:
        tool = self._tools[function_call["name"]]
        output = tool(**json.loads(function_call["arguments"]))
        return FunctionMessage(
            name=function_call["name"],
            content=str(output), 
        )







def multiply(a: int, b: int) -> int:
    """Multiple two integers and returns the result integer"""
    return a * b


multiply_tool = FunctionTool.from_defaults(fn=multiply)

def add(a: int, b: int) -> int:
    """Add two integers and returns the result integer"""
    return a + b

add_tool = FunctionTool.from_defaults(fn=add)

def postgresql_tool(query: str):
    """Input a query, it will Fetch data through postgresql"""
    return cur(query)

agent = YourOpenAIAgent(tools=[multiply_tool, add_tool, postgresql_tool])