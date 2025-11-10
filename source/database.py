import psycopg2

def get_db():
    return psycopg2.connect(
        host='localhost',
        database='return_management',
        user='postgres',
        password='0817',
        port='5432'
    )