import os
from dotenv import load_dotenv
from langchain.utilities import SerpAPIWrapper
from langchain.agents import initialize_agent, AgentType
from langchain.llms import OpenAI
from langchain.agents import load_tools
import openai

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

llm = OpenAI(temperature=0.9, max_tokens=100)
tools = load_tools(["requests_all"], llm=llm)


agent = initialize_agent(agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, tools=tools, llm=llm, verbose=True)

if(__name__ == "__main__"):
    while(True):
        a = input("Enter a query: ")
        if(a == "exit"):
            break
        print(agent.run(a))