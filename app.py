import os
from flask import Flask, render_template, request, redirect, url_for, flash
from models import get_products, get_product_by_name, add_order
from dotenv import load_dotenv
import psycopg2
from flask_mail import Mail, Message

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Secret key for session management and flash messages

# Get the DATABASE_URL from the environment variables
DB_URI = os.getenv('DATABASE_URI')

if not DB_URI:
    print("DATABASE_URL is not set. Please ensure it is defined in your .env file.")

# Database connection function
def get_db_connection():
    try:
        conn = psycopg2.connect(DB_URI)
        return conn
    except Exception as e:
        print(f"Unable to connect to the database: {e}")
        return None
    
@app.route('/')
def welcome():
    return render_template('welcome.html')


# Home Route - Displays all products
@app.route('/home')
def home():
    products = get_products()  # Fetch all products from the database
    return render_template('home.html', products=products)

# Cart Route - Displays the product added to the cart
@app.route('/cart/<string:product_name>', methods=['GET'])
def cart(product_name):
    product = get_product_by_name(product_name)  # Fetch product by name
    if not product:
        flash("Product not found!", "danger")
        return redirect(url_for('home'))
    return render_template('cart.html', product=product)  # Render cart page with product details

# Proceed to Payment Route - Displays payment page after adding product to cart
@app.route('/proceed_to_payment/<string:product_name>', methods=['POST'])
def proceed_to_payment(product_name):
    return redirect(url_for('payment', product_name=product_name))

# Payment Route - User selects a payment method
@app.route('/payment/<string:product_name>', methods=['GET', 'POST'])
def payment(product_name):
    if request.method == 'POST':
        # Check if 'payment_method' is in the form
        payment_method = request.form.get('payment_method')
        
        if not payment_method:
            flash("Please select a payment method.", "danger")
            return redirect(url_for('payment', product_name=product_name))

        # Process payment (this is a mock in this case)
        payment_successful = True  # Assume payment is successful

        if payment_successful:
            flash(f"Payment via {payment_method} successful!", "success")
            return redirect(url_for('home'))  # Redirect to home after successful payment
        else:
            flash("Payment failed. Please try again.", "danger")
            return redirect(url_for('payment', product_name=product_name))

    return render_template('payment.html', product_name=product_name)


# Order Confirmation Route - Display the order confirmation details
@app.route('/order-confirmed/<int:order_id>', methods=['GET'])
def order_confirmed(order_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch the order details using the order ID
    cursor.execute("SELECT * FROM orders WHERE id = %s", (order_id,))
    order = cursor.fetchone()
    conn.close()

    if order:
        return render_template('order_confirmed.html', order={
            'id': order[0],
            'product_name': order[1],
            'customer_name': order[2],
            'customer_email': order[3],
            'customer_address': order[4],
            'customer_phone': order[5],
            'total_price': order[6]
        })
    else:
        flash("Order not found!", "danger")
        return redirect(url_for('home'))

# Main entry point to run the app
if __name__ == '__main__':
    app.run(debug=True)
