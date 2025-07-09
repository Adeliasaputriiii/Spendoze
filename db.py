import pyodbc
import os
from dotenv import load_dotenv

load_dotenv() 

def get_db_connection():
    driver = os.getenv('DB_DRIVER')
    server = os.getenv('DB_SERVER')
    db = os.getenv('DB_NAME')
    user = os.getenv('DB_USER')
    pwd = os.getenv('DB_PASSWORD')

    connection_string = (
        f"DRIVER={{{driver}}};"
        f"SERVER={server};"
        f"DATABASE={db};"
        f"UID={user};"
        f"PWD={pwd};"
    )

    return pyodbc.connect(connection_string)
