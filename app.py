from flask import Flask, request, jsonify
from tinydb import TinyDB, Query
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import logging

app = Flask(__name__)
CORS(app)

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize TinyDB and specify the JSON file where the data will be stored
db = TinyDB('db.json')
admins_table = db.table('admins')
products_table = db.table('products')
transactions_table = db.table('transactions')

# Function to add initial admin data if the database is empty
def initialize_db():
    if not admins_table.all():
        logger.debug("Initializing database with default admin data and dummy entries...")
        # Insert initial admin data
        admins_table.insert_multiple([
            {"username": "admin1", "password": generate_password_hash("password1"), "adminId": "admin1"},
            {"username": "admin2", "password": generate_password_hash("password2"), "adminId": "admin2"}
        ])
        
        # Insert dummy product data for admin1 and admin2
        dummy_products_admin1 = [
            {"id": 1, "name": "Dummy Product 1", "price": 10.0, "description": "A dummy product", "barcode": "123456", "frontImage": "", "backImage": "", "quantity": 100, "adminId": "admin1"},
            {"id": 2, "name": "Dummy Product 2", "price": 20.0, "description": "Another dummy product", "barcode": "654321", "frontImage": "", "backImage": "", "quantity": 200, "adminId": "admin1"},
        ]
        dummy_products_admin2 = [
            {"id": 3, "name": "Admin2 Product 1", "price": 15.0, "description": "Admin2's first product", "barcode": "111222", "frontImage": "", "backImage": "", "quantity": 150, "adminId": "admin2"},
            {"id": 4, "name": "Admin2 Product 2", "price": 25.0, "description": "Admin2's second product", "barcode": "333444", "frontImage": "", "backImage": "", "quantity": 250, "adminId": "admin2"},
        ]
        products_table.insert_multiple(dummy_products_admin1)
        products_table.insert_multiple(dummy_products_admin2)
        
        # Insert dummy transaction data for admin1 and admin2
        dummy_transactions_admin1 = [
            {"id": 1, "customerName": "John Doe", "items": dummy_products_admin1[:1], "total": 10.0, "adminId": "admin1"},
            {"id": 2, "customerName": "Jane Smith", "items": dummy_products_admin1[1:], "total": 20.0, "adminId": "admin1"},
        ]
        dummy_transactions_admin2 = [
            {"id": 3, "customerName": "Alice Johnson", "items": dummy_products_admin2[:1], "total": 15.0, "adminId": "admin2"},
            {"id": 4, "customerName": "Bob Brown", "items": dummy_products_admin2[1:], "total": 25.0, "adminId": "admin2"},
        ]
        transactions_table.insert_multiple(dummy_transactions_admin1)
        transactions_table.insert_multiple(dummy_transactions_admin2)
        
        logger.debug("Database initialized with dummy entries.")

# Call the initialization function
initialize_db()

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    logger.debug(f"Received login data: {data}")
    
    if not username or not password:
        logger.warning("Login attempt with missing username or password.")
        return jsonify({"error": "Username and password are required"}), 400
    
    admin = admins_table.get(Query().username == username)
    
    logger.debug(f"User found: {admin}")
    
    if admin and check_password_hash(admin['password'], password):
        logger.debug(f"Login successful for username: {username}")
        return jsonify({"message": "Login successful", "adminId": admin['adminId']}), 200
    else:
        logger.warning(f"Invalid login attempt for username: {username}")
        return jsonify({"error": "Invalid username or password"}), 401

@app.route('/api/products/<admin_id>', methods=['GET'])
def get_products(admin_id):
    try:
        logger.debug(f"Fetching products for admin ID: {admin_id}")
        products = products_table.search(Query().adminId == admin_id)
        logger.debug(f"Products found: {products}")
        return jsonify({"products": products}), 200
    except Exception as e:
        logger.error(f"Error fetching products for admin {admin_id}: {e}")
        return jsonify({"error": "An error occurred while fetching products."}), 500

@app.route('/api/products/<admin_id>', methods=['POST'])
def add_product(admin_id):
    try:
        products_data = request.json.get('products', [])
        
        # Clear existing products for this adminId
        products_table.remove(Query().adminId == admin_id)
        
        # Insert new products with adminId included
        for product in products_data:
            product['adminId'] = admin_id
            products_table.insert(product)
        
        logger.debug(f"Products updated for admin ID: {admin_id}")
        return jsonify({"message": "Products updated successfully"}), 200
    except ValueError as ve:
        logger.warning(f"ValueError: {ve}")
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        logger.error(f"Error adding product for admin {admin_id}: {e}")
        return jsonify({"error": "An error occurred while adding the products."}), 500

@app.route('/api/transactions/<admin_id>', methods=['GET'])
def get_transactions(admin_id):
    try:
        logger.debug(f"Fetching transactions for admin ID: {admin_id}")
        transactions = transactions_table.search(Query().adminId == admin_id)
        logger.debug(f"Transactions found: {transactions}")
        return jsonify(transactions), 200
    except Exception as e:
        logger.error(f"Error fetching transactions for admin {admin_id}: {e}")
        return jsonify({"error": "An error occurred while fetching transactions."}), 500

@app.route('/api/transactions/<admin_id>', methods=['POST'])
def add_transaction(admin_id):
    try:
        transaction = request.json
        if not transaction:
            raise ValueError("No transaction data provided")
        
        logger.debug(f"Adding transaction for admin ID: {admin_id}")
        logger.debug(f"Transaction data: {transaction}")
        
        transaction['adminId'] = admin_id
        transactions_table.insert(transaction)
        logger.debug(f"Transaction added: {transaction}")
        return jsonify(transaction), 201
    except ValueError as ve:
        logger.warning(f"ValueError: {ve}")
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        logger.error(f"Error adding transaction for admin {admin_id}: {e}")
        return jsonify({"error": "An error occurred while adding the transaction."}), 500

if __name__ == '__main__':
    app.run(debug=True)
