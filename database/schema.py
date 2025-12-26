import os
import sys
from pathlib import Path
from dotenv import load_dotenv
CURRENT = Path(__file__).resolve()
PROJECT_ROOT = CURRENT.parents[1]
sys.path.append(str(PROJECT_ROOT))
load_dotenv(PROJECT_ROOT / ".env")
import psycopg2
from urllib.parse import urlparse, parse_qs
url = os.getenv("CONNECTION_STRING")
result = urlparse(url)
query_params = parse_qs(result.query)
sslmode = query_params.get("sslmode", ["require"])[0]


conn = psycopg2.connect(
    dbname=result.path[1:],  
    user=result.username,
    password=result.password,
    host=result.hostname,
    port=result.port or 5432,
    sslmode=sslmode
)

cur = conn.cursor()
cur.execute("SELECT version();")
print(cur.fetchone())

cur.close()
conn.close()
