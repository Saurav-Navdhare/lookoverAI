query="SELECT SUM(fixed_price) AS total_cost FROM public.aws_ec2_reserved_instances"
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
conn = psycopg2.connect(os.getenv("DB_URI"))
cur = conn.cursor()

cur.execute(query)

print(cur.fetchone())