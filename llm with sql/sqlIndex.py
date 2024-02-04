from llama_index import download_loader

DatabaseReader = download_loader('DatabaseReader')

reader = DatabaseReader(
    scheme = "postgresql", # Database Scheme
    host = "lookover-ai-test-1.cf3alghuei5c.ap-south-1.rds.amazonaws.com", # Database Host
    port = "5432", # Database Port
    user = "postgres", # Database User
    password = "YQwoegl8YOk4k6Drym3748zzy11g", # Database Password
    dbname = "postgres", # Database Name
)

query = f"""
Get me number of tables
"""

documents = reader.load_data(query=query)