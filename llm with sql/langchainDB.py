import os
import langchain
import openai
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

db = langchain.SQLDatabase.from_uri(os.getenv("DB_URI"))

llm = openai.Completion.create(engine="davinci", temperature=0, max_tokens=100)

chain = langchain.chains.SQLDatabaseChain.from_llm(llm, db)

result = chain.query("How many ec2 instances are running?")

print(result)