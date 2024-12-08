import psycopg2
from psycopg2 import sql

# Database connection utility
def get_db_connection():
    conn = psycopg2.connect(
        host="dpg-ct67d3tds78s73bth3bg-a.oregon-postgres.render.com",  # Change to your DB host
        database="kitab_db",  # Your database name
        user="kitab_db_user",  # Your DB username
        password="4dtlOKLDYGH4J0arZf8AsqTQlMCWWhGx"  # Your DB password
    )
    return conn

# Get all products from the database
def get_products():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    conn.close()
    return products

# Get a product by its name
def get_product_by_name(product_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE name = %s", (product_name,))
    product = cursor.fetchone()
    conn.close()
    return product

# Add an order to the orders table
def add_order(product_name, customer_name, customer_email, customer_address, customer_phone):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO orders (product_name, customer_name, customer_email, customer_address, customer_phone, total_price, payment_status)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (product_name, customer_name, customer_email, customer_address, customer_phone, 0.0, False))  # Replace 0.0 with actual price logic
    conn.commit()
    conn.close()

# Add a new product to the products table
def add_product(name, price, image_url):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO products (name, price, image_url)
    VALUES (%s, %s, %s)
    """, (name, price, image_url))
    conn.commit()
    conn.close()
