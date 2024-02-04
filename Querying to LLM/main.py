# importing the required modules
import psycopg2
from llama_index import VectorStoreIndex, SimpleDirectoryReader
from dotenv import load_dotenv
import openai
import os
from datetime import datetime
import gradio as gr

# load the environment variables
load_dotenv()
DB_URI=os.getenv("DB_URI")
openai.api_key=os.getenv("OPENAI_API_KEY")

# load the data and create the index
documents = SimpleDirectoryReader('cloudquery').load_data()
index = VectorStoreIndex.from_documents(documents)
query_engine = index.as_query_engine()

# define the query executor
def query_executor(query):
    start_time = datetime.now()
    response = query_engine.query(f" from the given data, give me a postgresql query to know {query}")
    print(response)
    # few shots to make the model understand the context
    prompt = f"""
    convert the key of JSON is in capitalized form
    give the query as output nothing else
    Q:
    SELECT COUNT(*) 
    FROM public.aws_ec2_instances 
    WHERE state->>'name' = 'running';

    A: 
    SELECT COUNT(*) 
    FROM public.aws_ec2_instances 
    WHERE state->>'Name' = 'running';

    Q:
    {str(response)}
    A:
    """

    # call openai llm
    query_response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        temperature=0,
        max_tokens=100
    )

    query_response = query_response.choices[0].text

    conn = psycopg2.connect(DB_URI)
    cur = conn.cursor()
    print
    cur.execute(str(query_response))
    query_time = (datetime.now() - start_time)
    return str(cur.fetchone()[0]), f"{query_time}s"
    # return str(query_response), f"{query_time}s"

# define the gradio interface
inputs = gr.components.Textbox(label="Enter Query")
outputs = [gr.components.Textbox(label="Output"), gr.components.Textbox(label="Time taken")]
demo = gr.Interface(fn=query_executor, inputs=inputs, outputs=outputs)

# launch the gradio interface
demo.launch(debug=True)