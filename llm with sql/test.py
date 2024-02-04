import psycopg2
from dotenv import load_dotenv
import openai
import os
from llama_index import VectorStoreIndex, SimpleDirectoryReader

# load the environment variables
load_dotenv()
DB_URI=os.getenv("DB_URI")
openai.api_key=os.getenv("OPENAI_API_KEY")

documents = SimpleDirectoryReader('cloudquery').load_data()
index = VectorStoreIndex.from_documents(documents)

query_engine = index.as_query_engine()

def query_executor(query):
    response = query_engine.query(f" from the given data, give me a postgresql query to know {query}")
    print(response)

print(query_engine.query("from the given data, give me a postgresql query to know cost of any ec2 instance, take anyone instance from the given data"))