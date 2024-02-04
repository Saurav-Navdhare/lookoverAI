import os
from dotenv import load_dotenv
from langchain.utilities import SerpAPIWrapper
from langchain.agents import initialize_agent, AgentType
from langchain.llms import OpenAI
from langchain.agents import load_tools
import openai

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

tools = load_tools(["serpapi"])

llm = OpenAI(model="gpt-4", temperature=0, openai_api_key=os.getenv("OPENAI_API_KEY"))


up_to_secure = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# Query the agent
# Basic Structure of the program
response = up_to_secure("Get me the lastest report of lastest hack of Iranian Group on Saudi Arabia Company") 
# print(response)