from llama_index import VectorStoreIndex, SimpleDirectoryReader
from langchain.agents import initialize_agent, AgentType
from langchain.sql_database import SQLDatabase
from langchain.llms import OpenAI
from langchain.tools import BaseTool
from sqlalchemy import create_engine
from llama_index.indices.struct_store.sql_query import *
import psycopg2

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

tools = [
    ec2_query,
    s3_query,
    cost_query
]

agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION
)

def get_outputs(query, DB_URI):
  try:
    conn = psycopg2.connect(DB_URI)
    conn.close()
  except Exception as e:
    print("Error: ", e) #log this error
    return "Check your DB_URI"
  # response = llm(f"If the given query is not related to aws (Amazon Web Services) then constraint the output with exact message, message: 'Only cloud related Queries are allowed', Else return the query back, query: {query}")
  # if " ".join(response.split()) == "Only cloud related Queries are allowed.":
  #   return "Only cloud related Queries are allowed."
  tables = agent.run(f"Give me table names which may store the information of {query}. Look answers in Get AWS Cost Data, Get AWS EC2 Data and Get AWS S3 Data, give table name separated by spaces and nothing else, if no tables found return empty string")
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

if(__name__ == "__main__"):
  print(get_outputs("how many instances are running in the region us-east-1", "postgresql://postgres:YQwoegl8YOk4k6Drym3748zzy11g@lookover-ai-test-1.cf3alghuei5c.ap-south-1.rds.amazonaws.com:5432/postgres"))