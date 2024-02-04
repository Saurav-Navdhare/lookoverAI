import psycopg2
from dotenv import load_dotenv
from os import getenv
import openai

load_dotenv()

from llama_index.node_parser.simple import SimpleNodeParser
from llama_index import ServiceContext, LLMPredictor
from llama_index.storage import StorageContext
from llama_index.langchain_helpers.text_splitter import TokenTextSplitter
from langchain.chat_models import ChatOpenAI


openai.api_key = getenv("OPENAI_API_KEY")
DB_URI = getenv("DB_URI")

conn = psycopg2.connect(DB_URI)
cur = conn.cursor()

chunk_size = 2048
llm_predictor = LLMPredictor(llm=ChatOpenAI(temperature=0, streaming=True, model_name="gpt-3.5-turbo"))
service_context = ServiceContext.from_defaults(chunk_size=chunk_size, llm_predictor=llm_predictor)
text_splitter = TokenTextSplitter(chunk_size=chunk_size)
node_parser = SimpleNodeParser(text_splitter=text_splitter)

from sqlalchemy import create_engine, MetaData, Table, Column, String, Integer, select, column

engine = create_engine(DB_URI)
metadata_obj = MetaData()

metadata_obj.create_all(engine)