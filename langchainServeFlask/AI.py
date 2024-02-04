from llama_index import VectorStoreIndex, SimpleDirectoryReader
from langchain.agents import initialize_agent, AgentType, load_tools
from langchain.sql_database import SQLDatabase
from langchain.llms import OpenAI
from langchain.tools import BaseTool
from sqlalchemy import create_engine
from llama_index.indices.struct_store.sql_query import *
import psycopg2
import os
from dotenv import load_dotenv
import openai
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

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

llm = OpenAI(temperature=0, openai_api_key=os.getenv("OPENAI_API_KEY"))
tools = load_tools(["llm-math"], llm=llm)

tools.extend([
    ec2_query,
    s3_query,
    cost_query
])

agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)


def get_outputs(query, DB_URI):
  try:
    conn = psycopg2.connect(DB_URI)
    conn.close()
  except Exception as e:
    print("Error: ", e) #log this error
    return "Check your DB_URI"
  tables = agent.run(f"Look answers in Get AWS Cost Data, Get AWS EC2 Data and Get AWS S3 Data, give table name separated by spaces and nothing else, if no tables found return empty string. If the query is about the cost than make sure to extract table name that stores cost per unit from Cost agent and table that stores uptime from EC2 or S3 or both whichever is mentioned in the query then multiply it using llm math. Give me table names which may store the information of {query}.")
  if(tables == ""):
    return "No cloud related output found for the given query"
  tables = tables.split(" ")
  if(len(tables) == 0 or tables[0] == ""):
    return "No cloud related output found for the given query"
  engine = create_engine(DB_URI)
  sql_database = SQLDatabase(engine, include_tables=tables)

  query_engine = NLSQLTableQueryEngine(
    sql_database=sql_database,
    tables = tables
  )
  response = query_engine.query((f"{query}? Use JOIN if required, avoid ambiguity, dont make query syntactical error, first check then execute"))
  return response

a = input("Enter query: ")
while(a!="exit"):
  print(get_outputs(a,  "postgresql://postgres:YQwoegl8YOk4k6Drym3748zzy11g@lookover-ai-test-1.cf3alghuei5c.ap-south-1.rds.amazonaws.com:5432/postgres"))
  a = input("Enter query: ")