import os
from dotenv import load_dotenv
import os
from embedchain import App
from serpapi import GoogleSearch

load_dotenv()
serpapi_key = os.getenv("SERPAPI_API_KEY")
search_engine = "google"

def get_urls(query) -> list:
    params = {
        "q": query,
        "api_key": serpapi_key,
        "engine": search_engine,
        "google_domain": "google.com",
        "hl": "en",
        "gl": "us",
        "num": 20,
        "safe": "active"
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    urls = []
    if 'organic_results' in results:
        for result in results['organic_results']:
            urls.append(result['link'])

    return urls
def write_config():
    config = """
    llm:
      provider: openai
      config:
        model: gpt-3.5-turbo
        temperature: 0.5
        max_tokens: 1000
        top_p: 1
        stream: false

    embedder:
      provider: openai
      config:
        model: text-embedding-ada-002
        deployment_name: ec_embeddings_ada_002
    """

    # Write the multi-line string to a YAML file
    with open('openai.yaml', 'w') as file:
        file.write(config)

def query_me(query: str):
    urls = get_urls(query)
    app = App.from_config(yaml_path="openai.yaml")
    for url in urls:
      app.add(url)
    return app

if __name__ == "__main__":
    write_config()
    query = input("Enter your query: ")
    query_engine = query_me(query)

    while(True):
        query_engine.query(query)
        print(query_engine.response)
        query = input("Enter your query: ")
        if(query == "exit"):
            break