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

print("hit")

openai.api_key = os.getenv("OPENAI_API_KEY")

cost = SimpleDirectoryReader("cost").load_data()
cost_index = VectorStoreIndex.from_documents(cost)

cloud_data = SimpleDirectoryReader("clouddata").load_data()
cloud_data_index = VectorStoreIndex.from_documents(cloud_data)

cost_engine = cost_index.as_query_engine()
cloud_data_engine = cloud_data_index.as_query_engine()

class GetAWSServiceData(BaseTool):
  name="Get AWS Service Data"
  description="Useful when you need to get table names from a postgresql database, the table name can be used to extract uptime/requests of aws services"

  def _run(self, text: str):
    response = cloud_data_engine.query(f"from the given data, give me a table names in which the following data may be stored: {text}")
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


cloud_data_query = GetAWSServiceData()
cost_query = GetAWSCostData()

llm = OpenAI(temperature=0, openai_api_key=os.getenv("OPENAI_API_KEY"))
tools = load_tools(["llm-math"], llm=llm)

tools.extend([
    cloud_data_query,
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
  tables = agent.run(f"Look answers in Get AWS Cost Data, Get AWS Service Data, give table name separated by spaces and nothing else, if no tables found return empty string. If the query is about the cost than make sure to extract table name that stores cost per unit from Cost agent and table that stores uptime or requests from AWS service. Give me table names which may store the information of {query}.")
  if(tables == ""):
    return "No cloud related output found for the given query"
  tables = tables.split(" ")
  if(len(tables) == 0 or tables[0] == ""):
    return "No cloud related output found for the given query"
  print(tables)
  # engine = create_engine(DB_URI)
  # sql_database = SQLDatabase(engine, include_tables=tables)

  # query_engine = NLSQLTableQueryEngine(
  #   sql_database=sql_database,
  #   tables = tables
  # )
  # response = query_engine.query((f"{query}? Use JOIN if required, avoid ambiguity, dont make query syntactical error, first check then execute"))
  # return response
  return tables

# if(__name__ == "__main__"):
#   print(get_outputs("how many instances are running in the region us-east-1", "postgresql://postgres:YQwoegl8YOk4k6Drym3748zzy11g@lookover-ai-test-1.cf3alghuei5c.ap-south-1.rds.amazonaws.com:5432/postgres"))

a = input("Enter query: ")
while(a!="exit"):
  print(get_outputs(a,  "postgresql://postgres:YQwoegl8YOk4k6Drym3748zzy11g@lookover-ai-test-1.cf3alghuei5c.ap-south-1.rds.amazonaws.com:5432/postgres"))
  a = input("Enter query: ")