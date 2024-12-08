import psycopg2

def get_db_connection():
    conn = psycopg2.connect(
        dbname='kitab_db', user='kitab_db_user', password='4dtlOKLDYGH4J0arZf8AsqTQlMCWWhGx', host='dpg-ct67d3tds78s73bth3bg-a.oregon-postgres.render.com', port='5432', sslmode= 'require')
    return conn



