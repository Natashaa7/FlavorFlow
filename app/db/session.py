import psycopg2
from psycopg2.extras import RealDictCursor

def get_db_connection():
    conn = psycopg2.connect(
        dbname="flavorflow",
        user="natashababu",
        password=None,
        host="localhost",
        port="5432",
        cursor_factory=RealDictCursor   #return query as python dictionaries
    )
    print("Database connected")   # prints when connection is successful
    return conn
