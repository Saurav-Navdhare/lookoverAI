#!/usr/bin/env python3
from llama_index import VectorStoreIndex, SimpleDirectoryReader
import os
from dotenv import load_dotenv
import openai
from langchain.agents import Tool, load_tools, initialize_agent, AgentType, create_sql_agent, AgentExecutor
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.sql_database import SQLDatabase
from langchain.llms import OpenAI
from langchain.tools import BaseTool
from sqlalchemy import create_engine
from llama_index.indices.struct_store.sql_query import *

load_dotenv()

# os.environ["OPENAI_API_KEY"] = "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"
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
DB_URI=os.getenv("DB_URI")
openai.api_key=os.getenv("OPENAI_API_KEY")

cost = SimpleDirectoryReader("cost").load_data()
cost_index = VectorStoreIndex.from_documents(cost)

ec2 = SimpleDirectoryReader("ec2").load_data()
ec2_index = VectorStoreIndex.from_documents(ec2)

s3 = SimpleDirectoryReader("s3").load_data()
s3_index = VectorStoreIndex.from_documents(s3)

cost_engine = cost_index.as_query_engine()
ec2_engine = ec2_index.as_query_engine()
s3_engine = s3_index.as_query_engine()

class GetAWSEC2Data(BaseTool):
  name="Get AWS EC2 Data"
  description="Useful when you need to get table names from a postgresql database, the table name can be used to extract data of aws ec2 services"

  def _run(self, text: str):
    response = ec2_engine.query(f"from the given data, give me a table names in which the following data may be stored: {text}")
    return str(response)

  def _arun(self, text: str):
    raise NotImplementedError("This tool does not support Async")

class GetAWSS3Data(BaseTool):
  name="Get AWS S3 Data"
  description="Useful when you need to get table names from a postgresql database, the table name can be used to extract data of aws s3 services"

  def _run(self, text: str):
    response = s3_engine.query(f"from the given data, give me a table names in which the following data may be stored: {text}")
    return str(response)

  def _arun(self, text: str):
    raise NotImplementedError("This tool does not support Async")

class GetAWSCostData(BaseTool):
  name="Get AWS Cost Data"
  description="Useful when you need to get table names from a postgresql database, the table name can be used to extract cost per hour or cost per unit data of aws services"

  def _run(self, text: str):
    response = cost_engine.query(f"from the given data, give me a table names in which the following data may be stored: {text}")
    return str(response)

  def _arun(self, text: str):
    raise NotImplementedError("This tool does not support Async")


ec2_query = GetAWSEC2Data()
s3_query = GetAWSS3Data()
cost_query = GetAWSCostData()

llm = OpenAI(temperature=0.2, openai_api_key=os.getenv("OPENAI_API_KEY"), model="gpt-4")

# tools = load_tools(["llm-math"], llm=llm)
tools = [
    ec2_query,
    s3_query,
    cost_query
]
# tools.insert(0, aws_agent)
agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

def get_outputs(query):

  tables = agent.run(f"Give me table names which may store the information of {query}. Look answers in Get AWS Cost Data, Get AWS EC2 Data and Get AWS S3 Data, give table name separated by spaces and nothing else, if no tables found return empty string")
  print("Tables: ", tables)
  tables = tables.split(" ")
  if(len(tables) == 0):
    return print("No tables found")
  engine = create_engine(DB_URI)
  sql_database = SQLDatabase(engine, include_tables=tables)

  query_engine = NLSQLTableQueryEngine(
    sql_database=sql_database,
    tables = tables
  )

  response = query_engine.query((f"{query}? Use JOIN if required, avoid ambiguity, dont make query syntactical error, first check then execute"))
  print(response)

while(True):
  print("---------------------------------------------------")
  query = input("Enter query: ")
  if(len(query.split()) == 0):
    exit
  if(query.split(" ")[0] == "exit"):
    break
  try:
    get_outputs(query)
  except Exception as e:
    print(e)
    print("This service is under development, it may not work for Complex queries, try simple queries")
  finally:
    continue