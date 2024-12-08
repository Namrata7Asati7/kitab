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

# Home Route - Displays all products
@app.route('/')
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

# Checkout Route - Displays the checkout form
@app.route('/checkout', methods=['POST'])
def checkout():
    product_name = request.form['product_name']
    customer_name = request.form['customer_name']
    customer_email = request.form['customer_email']
    customer_address = request.form['customer_address']
    customer_phone = request.form['customer_phone']

    # Mock payment validation (replace with payment gateway integration)
    payment_successful = True  # Set this to `False` to simulate payment failure

    if payment_successful:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Add order to the database
            cursor.execute("SELECT price FROM products WHERE name = %s", (product_name,))
            product = cursor.fetchone()
            if product:
                total_price = product[0]
                cursor.execute("""
                    INSERT INTO orders (product_name, customer_name, customer_email, customer_address, customer_phone, total_price)
                    VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
                """, (product_name, customer_name, customer_email, customer_address, customer_phone, total_price))
                order_id = cursor.fetchone()[0]
                conn.commit()

                # Send Order Confirmation Email
                msg = Message('Order Confirmation', sender=app.config['MAIL_USERNAME'], recipients=[customer_email])
                msg.body = f"""
                Dear {customer_name},

                Thank you for your order! Here are your order details:
                - Product: {product_name}
                - Total Price: {total_price}

                Your order will be delivered to:
                {customer_address}

                For inquiries, contact us at support@example.com.

                Thank you for shopping with us!
                """
                mail.send(msg)

                # Redirect to Order Confirmation Page
                return redirect(url_for('order_confirmed', order_id=order_id))
            else:
                flash("Product not found. Order not placed.", "danger")
        except Exception as e:
            flash(f"Database error: {str(e)}", "danger")
        finally:
            conn.close()
    else:
        flash("Payment failed. Order not placed.", "danger")
    return redirect(url_for('home'))

# Payment Route - User selects a payment method
@app.route('/payment/<string:product_name>', methods=['GET', 'POST'])
def payment(product_name):
    if request.method == 'POST':
        payment_method = request.form['payment_method']  # Retrieve selected payment method
        
        # Here, we assume successful payment; in a real scenario, payment integration would occur
        flash(f"Payment via {payment_method} successful!", "success")
        
        # After successful payment, return to the home page
        return redirect(url_for('home'))

    return render_template('payment.html', product_name=product_name)

# Email Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')  # Your email
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')  # Your email password
mail = Mail(app)

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
