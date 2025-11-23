import psycopg2
from psycopg2.extras import RealDictCursor

def get_db():
    conn = psycopg2.connect(
        host='postgres',
        database='return_management',
        user='postgres',
        password='password',
        port='5432'
    )
    return conn