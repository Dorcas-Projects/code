from flask import Flask, render_template, request, flash, redirect, url_for, session, jsonify
import sqlite3 as sql
import hashlib
from datetime import datetime
import os
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for using flash messages
host = 'http://127.0.0.1:5000/'

def get_db_connection():
    connection = sql.connect('database.db')
    connection.row_factory = sql.Row
    return connection

def close_db_connection(conn):
    if conn:
        conn.close()
    return render_template('login.html')

#User Registration Functionality
@app.route('/create_buyer', methods=['GET'])
def navigate_create_buyer():  # Navigates to create seller page. Returns page
    return render_template('create_buyer.html')

@app.route('/create_seller', methods=['GET'])
def navigate_create_seller():  # Navigates to create seller page. Returns page
    return render_template('create_seller.html')

@app.route('/create_buyer', methods=['POST'])
def create_buyer():  # Create user request
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password1')
        password_confirm = request.form.get('password2')
        business_name = request.form.get('business_name')
        if password == password_confirm:
            if is_valid_new_user(email, password):
                insert_buyer(email, password, business_name)
                return render_template('login.html')
            else:
                flash('Email already has an account', 'error')
        else:
            flash('Passwords do not match', 'error')
    return render_template('create_buyer.html')

@app.route('/create_seller', methods=['POST'])
def create_seller():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password1')
        password_confirm = request.form.get('password2')
        business_name = request.form.get('business_name')
        bank_routing_number = request.form.get('bank_routing_number')
        bank_account_number = request.form.get('bank_account_number')
        balance = request.form.get('balance')
        if password == password_confirm:
            if is_valid_new_user(email, password):
                insert_seller(email, password, business_name, bank_routing_number, bank_account_number, balance)
                return render_template('login.html')
            else:
                flash('Email already has an account', 'error')
        else:
            flash('Passwords do not match', 'error')

    return render_template('create_buyer.html')

def is_valid_login(email, password):  # returns true if email & password in db, false otherwise
    connection = sql.connect('database.db')
    hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
    output = connection.execute('SELECT * FROM Users WHERE email = ? AND password = ?',
                                (email, hashed_password)).fetchone()
    if output:
        return True
    else:
        return False

def is_valid_new_user(email, password):  # returns true if email is valid. false otherwise
    # valid users must have:
    # correct email format (abc123@xyz.com)
    # email not already present in db
    # complex enough password (optional?)
    if "@" not in email:
        return False
    conn = get_db_connection()
    output = conn.execute('SELECT * FROM Users WHERE email = ?', (email,)).fetchone()
    if output:
        return False
    return True

def insert_buyer(email, password, business_name):  # Inserts new buyer into database
    conn = get_db_connection()
    hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
    cursor = conn.cursor()
    output = cursor.execute('INSERT INTO Users (email, password) VALUES (?, ?)', (email, hashed_password))
    output2 = cursor.execute('INSERT INTO Buyers (email, business_name, buyer_address_id) VALUES (?, ?, ?)',
                             (email, business_name, generate_new_buyer_address_id()))
    conn.commit()
    conn.close()
    return output2

def insert_seller(email, password, business_name, bank_routing_number, bank_account_number, balance): # insets new seller into database
    conn = get_db_connection()
    hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
    cursor = conn.cursor()
    output = cursor.execute('INSERT INTO Users (email, password) VALUES (?, ?)', (email, hashed_password))
    output2 = cursor.execute(
    'INSERT INTO Sellers (email, business_name, business_address_id, bank_routing_number, bank_account_number, balance) '
    'VALUES (?, ?, ?, ?, ?, ?)',
    (email, business_name, generate_new_seller_address_id() ,bank_routing_number, bank_account_number, balance))
    conn.commit()
    conn.close()
    return output2

def generate_new_buyer_address_id(): # Generates a new buyer_address_id
    conn = get_db_connection()
    new_address_id = 0
    output = conn.execute('SELECT buyer_address_id FROM Buyers WHERE buyer_address_id = ?', (new_address_id,)).fetchone()
    while output:
        new_address_id += 1
        output = conn.execute('SELECT buyer_address_id FROM Buyers WHERE buyer_address_id = ?',
                              (new_address_id,)).fetchone()
    return new_address_id

def generate_new_seller_address_id(): # Generates a new business_address_id
    conn = get_db_connection()
    new_address_id = 0
    output = conn.execute('SELECT business_address_id FROM Sellers WHERE business_address_id = ?', (new_address_id,)).fetchone()
    while output:
        new_address_id += 1
        output = conn.execute('SELECT business_address_id FROM Sellers WHERE business_address_id = ?',
                              (new_address_id,)).fetchone()
    return new_address_id


def is_buyer(email): # Checks if user login is buyer
    connection = sql.connect('database.db')
    output = connection.execute('SELECT * FROM Buyers WHERE email = ?', (email,)).fetchone()
    if output:
        return True
    else:
        return False

def is_seller(email): # Checks if user login is seller
    connection = sql.connect('database.db')
    output = connection.execute('SELECT * FROM Sellers WHERE email = ?', (email,)).fetchone()
    if output:
        return True
    else:
        return False

def is_helpdesk(email): #checks if user login is helpdesk
    connection = sql.connect('database.db')
    output = connection.execute('SELECT * FROM Helpdesk WHERE email = ?', (email,)).fetchone()
    if output:
        return True
    else:
        return False

# Functions for Category Hierarchy
def get_subcategories(parent_category): # Get all subcategories of a given category
    conn = get_db_connection()
    cursor = conn.execute('''
        SELECT category_name
        FROM Categories
        WHERE parent_category = ?
        ORDER BY category_name
    ''', (parent_category,))
    result = cursor.fetchall()
    conn.close()
    return result

def get_category_by_name(category_name): # Get category details by name
    conn = get_db_connection()
    cursor = conn.execute('''
        SELECT *
        FROM Categories
        WHERE category_name = ?
    ''', (category_name,))
    result = cursor.fetchone()
    conn.close()
    return result

def get_category_path(category_name): # Get the full path for a category
    if category_name == 'Root' or not category_name:
        return [{'name': 'Root', 'link': 'Root'}]
    path = []
    current = category_name
    conn = get_db_connection()
    while current != 'Root' and current is not None:
        cursor = conn.execute('''
            SELECT *
            FROM Categories
            WHERE category_name = ?
        ''', (current,))
        category = cursor.fetchone()
        if not category:
            break
        path.insert(0, {'name': current, 'link': current})
        current = category['parent_category']
    path.insert(0, {'name': 'Root', 'link': 'Root'})
    conn.close()
    return path

def gather_subcategories(parent): #recursive function to get all subcategories
    category = [parent]
    for row in get_subcategories(parent):
        child = row['category_name']
        category.extend(gather_subcategories(child))
    return category

def get_category_products(category_name): #get all products in a given category
    conn = get_db_connection()
    if category_name == 'Root':
        cursor = conn.execute('''
            SELECT seller_email, listing_id, product_name, product_description, quantity, product_price
            FROM Product_Listings
            WHERE status = 1 AND quantity > 0
            ORDER BY product_name
        ''')
    else:
        valid_categories = gather_subcategories(category_name)
        placeholders = ','.join('?' for _ in valid_categories)
        query = f'''
            SELECT seller_email, listing_id, product_name, product_description, quantity, product_price
            FROM Product_Listings
            WHERE category IN ({placeholders})
            AND status = 1
            AND quantity > 0
            ORDER BY product_name
        '''
        cursor = conn.execute(query, valid_categories)
    products = cursor.fetchall()
    conn.close()
    return products

# Product Listing Functionality
def get_product_details(seller_email, listing_id):
    """Get detailed information about a specific product."""
    conn = get_db_connection()
    cursor = conn.execute('''
        SELECT p.*, s.business_name as seller_name
        FROM Product_Listings p
        JOIN Sellers s ON p.seller_email = s.email
        WHERE p.seller_email = ? AND p.listing_id = ?
    ''', (seller_email, listing_id))
    result = cursor.fetchone()
    conn.close()
    return result

def get_product_reviews(seller_email, listing_id):
    """Get reviews for a specific product."""
    conn = get_db_connection()
    cursor = conn.execute('''
        SELECT r.review_desc, r.rating, o.buyer_email, o.date
        FROM Reviews r
        JOIN Orders o ON r.order_id = o.order_id
        WHERE o.seller_email = ? AND o.listing_id = ?
        ORDER BY o.date DESC
    ''', (seller_email, listing_id))
    result = cursor.fetchall()
    conn.close()
    return result

def search_products(query_text, min_price=None, max_price=None):
    """Search for products by name, description, or category."""
    conn = get_db_connection()
    # Base query
    sql_query = '''
    SELECT p.seller_email, p.listing_id, p.product_name,p.product_description, 
           p.product_price, p.quantity, s.business_name as seller_name
    FROM Product_Listings p
    JOIN Sellers s ON p.seller_email = s.email
    WHERE p.status = 1 AND p.quantity > 0
    '''
    params = []
    # Add text search if provided
    if query_text:
        sql_query += ''' AND (
            p.product_name LIKE ? OR 
            p.product_description LIKE ? OR 
            p.product_title LIKE ? OR
            p.category LIKE ? OR
            s.business_name LIKE ?
        )'''
        search_param = f'%{query_text}%'
        params.extend([search_param, search_param, search_param, search_param, search_param])
    # Add price filters if provided
    if min_price is not None:
        sql_query += ' AND p.product_price >= ?'
        params.append(min_price)
    if max_price is not None:
        sql_query += ' AND p.product_price <= ?'
        params.append(max_price)
    sql_query += ' ORDER BY p.product_name'
    cursor = conn.execute(sql_query, params)
    result = cursor.fetchall()
    conn.close()
    return result

def get_seller_information(seller_email):
    conn = get_db_connection()
    cursor = conn.execute('''
        SELECT email, business_name
        FROM Sellers
        WHERE email = ?
        ''', (seller_email,))
    result = cursor.fetchone()
    conn.close()
    return result

# Product Listing Management Functions
def get_seller_products(seller_email):
    """Get all products listed by a specific seller."""
    conn = get_db_connection()
    cursor = conn.execute('''
        SELECT listing_id, product_name, category, product_price, quantity, status
        FROM Product_Listings
        WHERE seller_email = ?
        ORDER BY status DESC, product_name
    ''', (seller_email,))
    result = cursor.fetchall()
    conn.close()
    return result

def get_next_listing_id(seller_email):
    """Get the next available listing ID for a seller."""
    conn = get_db_connection()
    cursor = conn.execute('''
        SELECT MAX(listing_id) as max_id
        FROM Product_Listings
        WHERE seller_email = ?
    ''', (seller_email,))
    result = cursor.fetchone()
    conn.close()
    
    if result and result['max_id'] is not None:
        return result['max_id'] + 1
    return 1

def create_product_listing(seller_email, category, product_title, product_name, 
                         product_description, quantity, product_price):
    """Create a new product listing."""
    listing_id = get_next_listing_id(seller_email)
    
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO Product_Listings (
            seller_email, listing_id, category, product_title, product_name, 
            product_description, quantity, product_price, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
    ''', (
        seller_email, listing_id, category, product_title, product_name,
        product_description, quantity, product_price
    ))
    conn.commit()
    conn.close()
    return listing_id

def update_product_listing(seller_email, listing_id, product_title, product_name, 
                          product_description, quantity, product_price, status=None):
    """Update an existing product listing."""
    conn = get_db_connection()
    
    if status is None:
        # If status isn't provided, maintain the current status
        conn.execute('''
            UPDATE Product_Listings
            SET product_title = ?, product_name = ?, product_description = ?,
                quantity = ?, product_price = ?
            WHERE seller_email = ? AND listing_id = ?
        ''', (
            product_title, product_name, product_description,
            quantity, product_price, seller_email, listing_id
        ))
    else:
        conn.execute('''
            UPDATE Product_Listings
            SET product_title = ?, product_name = ?, product_description = ?,
                quantity = ?, product_price = ?, status = ?
            WHERE seller_email = ? AND listing_id = ?
        ''', (
            product_title, product_name, product_description,
            quantity, product_price, status, seller_email, listing_id
        ))
    
    conn.commit()
    conn.close()

def delete_product_listing(seller_email, listing_id):
    """Set a product listing as inactive (status = 0)."""
    conn = get_db_connection()
    conn.execute('''
        UPDATE Product_Listings
        SET status = 0
        WHERE seller_email = ? AND listing_id = ?
    ''', (seller_email, listing_id))
    conn.commit()
    conn.close()

# Order Management Functions
def create_order(seller_email, listing_id, buyer_email, quantity, payment, date=None):
    """Create a new order."""
    if date is None:
        date = datetime.now().strftime('%Y-%m-%d')

    conn = get_db_connection()

    # Get the next order ID
    cursor = conn.execute("SELECT MAX(order_id) as max_id FROM Orders")
    result = cursor.fetchone()
    order_id = 1
    if result and result['max_id'] is not None:
        order_id = result['max_id'] + 1

    # Begin transaction
    conn.execute('BEGIN TRANSACTION')

    try:
        # Insert the order
        conn.execute('''
            INSERT INTO Orders (order_id, seller_email, listing_id, buyer_email, date, quantity, payment)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (order_id, seller_email, listing_id, buyer_email, date, quantity, payment))

        # Update product quantity
        conn.execute('''
            UPDATE Product_Listings
            SET quantity = quantity - ?
            WHERE seller_email = ? AND listing_id = ?
        ''', (quantity, seller_email, listing_id))

        # Check if product is sold out, update status if needed
        conn.execute('''
            UPDATE Product_Listings
            SET status = 2
            WHERE seller_email = ? AND listing_id = ? AND quantity <= 0
        ''', (seller_email, listing_id))

        # Update seller balance
        conn.execute('''
            UPDATE Sellers
            SET balance = balance + ?
            WHERE email = ?
        ''', (payment, seller_email))

        # Commit transaction
        conn.commit()
    except Exception as e:
        # Rollback in case of error
        conn.rollback()
        conn.close()
        raise e

    conn.close()
    return order_id

def get_order_details(order_id):
    """Get detailed information about a specific order."""
    conn = get_db_connection()
    cursor = conn.execute('''
        SELECT o.order_id, o.seller_email, o.listing_id, o.buyer_email, o.date, o.quantity, o.payment,
               p.product_name, p.product_description, s.business_name as seller_name
        FROM Orders o
        JOIN Product_Listings p ON o.seller_email = p.seller_email AND o.listing_id = p.listing_id
        JOIN Sellers s ON o.seller_email = s.email
        WHERE o.order_id = ?
    ''', (order_id,))
    result = cursor.fetchone()
    conn.close()
    return result

def get_buyer_orders(buyer_email):
    """Get all orders placed by a specific buyer."""
    conn = get_db_connection()
    cursor = conn.execute('''
        SELECT o.order_id, o.seller_email, o.listing_id, o.date, o.quantity, o.payment,
               p.product_name, s.business_name as seller_name,
               (SELECT COUNT(*) FROM Reviews WHERE order_id = o.order_id) as has_review
        FROM Orders o
        JOIN Product_Listings p ON o.seller_email = p.seller_email AND o.listing_id = p.listing_id
        JOIN Sellers s ON o.seller_email = s.email
        WHERE o.buyer_email = ?
        ORDER BY o.date DESC
    ''', (buyer_email,))
    result = cursor.fetchall()
    conn.close()
    return result

def get_seller_orders(seller_email):
    """Get all orders for products sold by a specific seller."""
    conn = get_db_connection()
    cursor = conn.execute('''
        SELECT o.order_id, o.buyer_email, o.listing_id, o.date, o.quantity, o.payment,
               p.product_name, b.business_name as buyer_name
        FROM Orders o
        JOIN Product_Listings p ON o.listing_id = p.listing_id AND o.seller_email = p.seller_email
        JOIN Buyers b ON o.buyer_email = b.email
        WHERE o.seller_email = ?
        ORDER BY o.date DESC
    ''', (seller_email,))
    result = cursor.fetchall()
    conn.close()
    return result

def create_product_review(order_id, review_text, rating):
    """Create a review for a purchased product."""
    conn = get_db_connection()
    
    # Check if review already exists
    cursor = conn.execute("SELECT * FROM Reviews WHERE order_id = ?", (order_id,))
    existing = cursor.fetchone()
    
    if existing:
        # Update existing review
        conn.execute('''
            UPDATE Reviews
            SET review_desc = ?, rating = ?
            WHERE order_id = ?
        ''', (review_text, rating, order_id))
    else:
        # Insert new review
        conn.execute('''
            INSERT INTO Reviews (order_id, review_desc, rating)
            VALUES (?, ?, ?)
        ''', (order_id, review_text, rating))
    
    conn.commit()
    conn.close()

# Shopping Cart Functions
def get_cart_items(buyer_email):
    """Get all items in a buyer's shopping cart."""
    conn = get_db_connection()
    
    # Check if cart table exists, create if not
    conn.execute('''
    CREATE TABLE IF NOT EXISTS Shopping_Cart (
        buyer_email TEXT,
        seller_email TEXT,
        listing_id INTEGER,
        quantity INTEGER,
        PRIMARY KEY (buyer_email, seller_email, listing_id),
        FOREIGN KEY (buyer_email) REFERENCES Buyers(email),
        FOREIGN KEY (seller_email, listing_id) REFERENCES Product_Listings(seller_email, listing_id)
    )
    ''')
    
    cursor = conn.execute('''
    SELECT c.seller_email, c.listing_id, c.quantity,
           p.product_name, p.product_price, p.quantity as available_quantity,
           s.business_name as seller_name
    FROM Shopping_Cart c
    JOIN Product_Listings p ON c.seller_email = p.seller_email AND c.listing_id = p.listing_id
    JOIN Sellers s ON c.seller_email = s.email
    WHERE c.buyer_email = ? AND p.status = 1
    ORDER BY p.product_name
    ''', (buyer_email,))
    
    result = cursor.fetchall()
    conn.close()
    return result

def add_to_cart(buyer_email, seller_email, listing_id, quantity):
    """Add an item to the shopping cart."""
    conn = get_db_connection()
    
    # Check if cart table exists, create if not
    conn.execute('''
    CREATE TABLE IF NOT EXISTS Shopping_Cart (
        buyer_email TEXT,
        seller_email TEXT,
        listing_id INTEGER,
        quantity INTEGER,
        PRIMARY KEY (buyer_email, seller_email, listing_id),
        FOREIGN KEY (buyer_email) REFERENCES Buyers(email),
        FOREIGN KEY (seller_email, listing_id) REFERENCES Product_Listings(seller_email, listing_id)
    )
    ''')
    
    # Check if the item is already in the cart
    cursor = conn.execute('''
    SELECT quantity
    FROM Shopping_Cart
    WHERE buyer_email = ? AND seller_email = ? AND listing_id = ?
    ''', (buyer_email, seller_email, listing_id))
    existing = cursor.fetchone()
    
    if existing:
        # Update quantity
        conn.execute('''
        UPDATE Shopping_Cart
        SET quantity = quantity + ?
        WHERE buyer_email = ? AND seller_email = ? AND listing_id = ?
        ''', (quantity, buyer_email, seller_email, listing_id))
    else:
        # Insert new item
        conn.execute('''
        INSERT INTO Shopping_Cart (buyer_email, seller_email, listing_id, quantity)
        VALUES (?, ?, ?, ?)
        ''', (buyer_email, seller_email, listing_id, quantity))
    
    conn.commit()
    conn.close()

def update_cart_quantity(buyer_email, seller_email, listing_id, quantity):
    """Update the quantity of an item in the shopping cart."""
    conn = get_db_connection()
    
    if quantity <= 0:
        # Remove item if quantity is 0 or negative
        remove_from_cart(buyer_email, seller_email, listing_id)
    else:
        conn.execute('''
        UPDATE Shopping_Cart
        SET quantity = ?
        WHERE buyer_email = ? AND seller_email = ? AND listing_id = ?
        ''', (quantity, buyer_email, seller_email, listing_id))
        conn.commit()
    
    conn.close()

def remove_from_cart(buyer_email, seller_email, listing_id):
    """Remove an item from the shopping cart."""
    conn = get_db_connection()
    conn.execute('''
    DELETE FROM Shopping_Cart
    WHERE buyer_email = ? AND seller_email = ? AND listing_id = ?
    ''', (buyer_email, seller_email, listing_id))
    conn.commit()
    conn.close()

def clear_cart(buyer_email):
    """Remove all items from a buyer's shopping cart."""
    conn = get_db_connection()
    conn.execute('''
    DELETE FROM Shopping_Cart
    WHERE buyer_email = ?
    ''', (buyer_email,))
    conn.commit()
    conn.close()

def checkout_cart(buyer_email):
    """Create orders for all items in the shopping cart."""
    conn = get_db_connection()
    conn.row_factory = sql.Row
    
    # Get cart items
    cursor = conn.execute('''
    SELECT c.seller_email, c.listing_id, c.quantity,
           p.product_name, p.product_price, p.quantity as available_quantity
    FROM Shopping_Cart c
    JOIN Product_Listings p ON c.seller_email = p.seller_email AND c.listing_id = p.listing_id
    WHERE c.buyer_email = ? AND p.status = 1
    ''', (buyer_email,))
    
    cart_items = cursor.fetchall()
    
    if not cart_items:
        conn.close()
        return []
    
    # Begin transaction
    conn.execute('BEGIN TRANSACTION')
    
    try:
        # Create orders for each item
        current_date = datetime.now().strftime('%Y-%m-%d')
        orders_created = []
        
        for item in cart_items:
            seller_email = item['seller_email']
            listing_id = item['listing_id']
            quantity = item['quantity']
            
            # Check availability
            if quantity > item['available_quantity']:
                raise ValueError(f"Not enough stock for {item['product_name']}. Only {item['available_quantity']} available.")
            
            # Calculate payment
            payment = item['product_price'] * quantity
            
            # Get next order ID
            cursor = conn.execute("SELECT MAX(order_id) as max_id FROM Orders")
            result = cursor.fetchone()
            order_id = 1 if result['max_id'] is None else result['max_id'] + 1
            
            # Create order
            conn.execute('''
                INSERT INTO Orders (order_id, seller_email, listing_id, buyer_email, date, quantity, payment)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (order_id, seller_email, listing_id, buyer_email, current_date, quantity, payment))
            
            # Update product quantity
            conn.execute('''
                UPDATE Product_Listings
                SET quantity = quantity - ?
                WHERE seller_email = ? AND listing_id = ?
            ''', (quantity, seller_email, listing_id))
            
            # Check if product is sold out
            conn.execute('''
                UPDATE Product_Listings
                SET status = 2
                WHERE seller_email = ? AND listing_id = ? AND quantity <= 0
            ''', (seller_email, listing_id))
            
            # Update seller balance
            conn.execute('''
                UPDATE Sellers
                SET balance = balance + ?
                WHERE email = ?
            ''', (payment, seller_email))
            
            orders_created.append(order_id)
        
        # Clear the cart
        conn.execute('''
            DELETE FROM Shopping_Cart
            WHERE buyer_email = ?
        ''', (buyer_email,))
        
        # Commit transaction
        conn.commit()
        
        conn.close()
        return orders_created
        
    except Exception as e:
        # Rollback in case of error
        conn.rollback()
        conn.close()
        raise e

def get_all_categories():
    """Get all categories."""
    conn = get_db_connection()
    cursor = conn.execute("SELECT * FROM Categories ORDER BY category_name")
    result = cursor.fetchall()
    conn.close()
    return result

def get_credit_cards(buyer_email):
    """Get all credit cards for a buyer."""
    conn = get_db_connection()
    cursor = conn.execute('''
        SELECT credit_card_num, card_type, expire_month, expire_year
        FROM Credit_Cards
        WHERE Owner_email = ?
    ''', (buyer_email,))
    result = cursor.fetchall()
    conn.close()
    return result
# Main Route Handlers
@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handles login requests."""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        if is_valid_login(email, password):
            # Login successful - store email in session
            session['email'] = email
            
            if is_buyer(email):
                session['is_buyer'] = True
                session['is_seller'] = False
                session['is_helpdesk'] = False
                return redirect(url_for('home'))
            elif is_seller(email):
                session['is_buyer'] = False
                session['is_seller'] = True
                session['is_helpdesk'] = False
                return redirect(url_for('home'))
            elif is_helpdesk(email):
                session['is_buyer'] = False
                session['is_seller'] = False
                session['is_helpdesk'] = True
                return redirect(url_for('home'))
        else:
            # Login failed - flash an error message
            flash('Login attempt failed. Invalid email or password.', 'error')
            return render_template('login.html')
    # If GET request, just show the login page
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logs out the user."""
    # Clear all session data
    session.clear()
    flash('You have been logged out successfully.')
    return redirect(url_for('index'))

@app.route('/buyer_personal_info')
def buyer_personal_info(): # Navigates to Buyer Personal Info page
    """Renders Personal Page for Buyer"""
    if not session.get('is_buyer', False):
        return redirect(url_for('home'))
    # Pass user's information to be displayed
    conn = get_db_connection()
    current_business_name = conn.execute("SELECT business_name FROM Buyers WHERE email = ?", (session['email'],)).fetchone()[0]
    return render_template('buyer_personal_info.html',
                           current_business_name=current_business_name)

@app.route('/seller_personal_info')
def seller_personal_info(): # Navigates to Seller Personal Info page
    """Renders Personal Page for Seller"""
    if not session.get('is_seller', False):
        return redirect(url_for('home'))
    # Pass user's information to be displayed
    conn = get_db_connection()
    current_business_name = conn.execute("SELECT business_name FROM Sellers WHERE email = ?", (session['email'],)).fetchone()[0]
    current_bank_routing_number = conn.execute("SELECT bank_routing_number FROM Sellers WHERE email = ?", (session['email'],)).fetchone()[0]
    current_bank_account_number = conn.execute("SELECT bank_account_number FROM Sellers WHERE email = ?", (session['email'],)).fetchone()[0]
    return render_template('seller_personal_info.html',
                           current_business_name=current_business_name,
                           current_bank_routing_number=current_bank_routing_number,
                           current_bank_account_number=current_bank_account_number)

@app.route('/update_buyer_personal_info', methods=['POST'])
def update_buyer_personal_info():
    """Updates Personal Information for Buyers"""
    password = request.form.get('password')
    business_name = request.form.get('business_name')
    # Update new information in table
    conn = get_db_connection()
    if password:
        hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
        output = conn.execute("UPDATE Users SET password = ? WHERE email = ?", (hashed_password, session['email']))
    if business_name:
        output = conn.execute("UPDATE Buyers SET business_name = ? WHERE email = ?", (business_name, session['email']))
    conn.commit()
    # Retrieve new information to display
    current_business_name = conn.execute("SELECT business_name FROM Buyers WHERE email = ?", (session['email'],)).fetchone()[0]
    conn.close()
    return render_template('buyer_personal_info.html',
                           current_business_name=current_business_name)

@app.route('/update_seller_personal_info', methods=['POST'])
def update_seller_personal_info():
    """Updates Personal Information for Sellers"""
    password = request.form.get('password')
    business_name = request.form.get('business_name')
    bank_routing_number = request.form.get('bank_routing_number')
    bank_account_number = request.form.get('bank_account_number')
    # Update new information in table
    conn = get_db_connection()
    if password:
        hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
        output = conn.execute("UPDATE Users SET password = ? WHERE email = ?", (hashed_password, session['email']))
    if business_name:
        output = conn.execute("UPDATE Sellers SET business_name = ? WHERE email = ?", (business_name, session['email']))
    if bank_routing_number:
        output = conn.execute("UPDATE Sellers SET bank_routing_number = ? WHERE email = ?", (bank_routing_number, session['email']))
    if bank_account_number:
        output = conn.execute("UPDATE Sellers SET bank_account_number = ? WHERE email = ?", (bank_account_number, session['email']))
    conn.commit()
    # Retrieve new information to display
    current_business_name = conn.execute("SELECT business_name FROM Sellers WHERE email = ?", (session['email'],)).fetchone()[0]
    current_bank_routing_number = conn.execute("SELECT bank_routing_number FROM Sellers WHERE email = ?", (session['email'],)).fetchone()[0]
    current_bank_account_number = conn.execute("SELECT bank_account_number FROM Sellers WHERE email = ?", (session['email'],)).fetchone()[0]
    conn.close()
    return render_template('seller_personal_info.html',
                           current_business_name=current_business_name,
                           current_bank_routing_number=current_bank_routing_number,
                           current_bank_account_number=current_bank_account_number)

# Category and Product Routes
@app.route('/categories')
def categories():
    """Display the category hierarchy and products within a category."""
    # Check if user is logged in
    if 'email' not in session:
        flash('Please log in to browse categories')
        return redirect(url_for('login'))
    
    # Get the parent category from the request, default to 'All'
    parent_category = request.args.get('parent', 'Root')
    
    # Get the current category details
    category = None
    if parent_category != 'Root':
        category = get_category_by_name(parent_category)

    # Get subcategories of the current category
    subcategories = get_subcategories(parent_category)
    
    # Get products in the current category
    products = get_category_products(parent_category)
    
    # Build breadcrumb path for navigation
    breadcrumb_path = get_category_path(parent_category)
    
    return render_template(
        'categories.html',
        current_category=parent_category,
        category=category,
        subcategories=subcategories,
        products=products,
        breadcrumb_path=breadcrumb_path
    )

@app.route('/product/<seller_email>/<int:listing_id>')
def product_detail(seller_email, listing_id):
    # Check if user is logged in
    if 'email' not in session:
        flash('Please log in to view product details')
        return redirect(url_for('login'))
    
    # Get the product details
    product = get_product_details(seller_email, listing_id)
    if not product:
        flash('Product not found')
        return redirect(url_for('categories'))
    
    # Get product reviews
    reviews = get_product_reviews(seller_email, listing_id)
    seller = get_seller_information(seller_email)

    # Calculate average rating
    avg_rating = 0
    if reviews:
        avg_rating = sum(review['rating'] for review in reviews) / len(reviews)
    
    # Get category path for breadcrumb navigation
    category_path = get_category_path(product['category'])
    
    return render_template(
        'product_detail.html',
        product=product,
        seller = seller,
        reviews=reviews,
        avg_rating=avg_rating,
        category_path=category_path
    )

@app.route('/search')
def search():
    """Search for products by name, description, or category."""
    # Get search parameters
    query = request.args.get('query', '')
    min_price = request.args.get('min_price', '')
    max_price = request.args.get('max_price', '')
    
    # Convert price parameters to float if provided
    min_price_val = float(min_price) if min_price else None
    max_price_val = float(max_price) if max_price else None
    
    # Perform search
    products = None
    if query or min_price or max_price:
        products = search_products(query, min_price_val, max_price_val)
    
    return render_template(
        'search.html',
        query=query,
        min_price=min_price,
        max_price=max_price,
        products=products
    )

# Product Management Routes
@app.route('/seller/products')
def seller_products():
    """Display all products listed by the seller."""
    # Check if user is logged in and is a seller
    if 'email' not in session:
        flash('Please log in to view your products')
        return redirect(url_for('login'))
    
    if not session.get('is_seller', False):
        flash('Only sellers can access this page')
        return redirect(url_for('home'))
    
    # Get all products for the seller
    seller_email = session['email']
    products = get_seller_products(seller_email)
    
    return render_template('seller_products.html', products=products)

@app.route('/seller/product/new', methods=['GET', 'POST'])
def new_product():
    """Create a new product listing."""
    # Check if user is logged in and is a seller
    if 'email' not in session:
        flash('Please log in to create a product')
        return redirect(url_for('login'))
    
    if not session.get('is_seller', False):
        flash('Only sellers can create products')
        return redirect(url_for('home'))
    
    # Handle form submission
    if request.method == 'POST':
        seller_email = session['email']
        category = request.form.get('category')
        product_title = request.form.get('product_title')
        product_name = request.form.get('product_name')
        product_description = request.form.get('product_description')
        quantity = int(request.form.get('quantity'))
        product_price = float(request.form.get('product_price'))
        
        # Create the product
        listing_id = create_product_listing(
            seller_email, category, product_title, product_name,
            product_description, quantity, product_price
        )
        
        flash(f'Product "{product_name}" created successfully')
        return redirect(url_for('seller_products'))
    
    # GET request - show the form
    # Get all categories for the dropdown
    categories = get_all_categories()
    
    return render_template('seller_product_form.html', 
                          categories=categories, 
                          product=None,
                          form_action=url_for('new_product'),
                          form_title='Create New Product')

@app.route('/seller/product/edit/<int:listing_id>', methods=['GET', 'POST'])
def edit_product(listing_id):
    """Edit an existing product listing."""
    # Check if user is logged in and is a seller
    if 'email' not in session:
        flash('Please log in to edit a product')
        return redirect(url_for('login'))
    
    if not session.get('is_seller', False):
        flash('Only sellers can edit products')
        return redirect(url_for('home'))

    seller_email = session['email']
    
    # Get the product details
    conn = get_db_connection()
    cursor = conn.execute('''
        SELECT *
        FROM Product_Listings
        WHERE seller_email = ? AND listing_id = ?
    ''', (seller_email, listing_id))
    product = cursor.fetchone()
    conn.close()
    
    if not product:
        flash('Product not found or you do not have permission to edit it')
        return redirect(url_for('seller_products'))
    
    # Handle form submission
    if request.method == 'POST':
        category = request.form.get('category')
        product_title = request.form.get('product_title')
        product_name = request.form.get('product_name')
        product_description = request.form.get('product_description')
        quantity = int(request.form.get('quantity'))
        product_price = float(request.form.get('product_price'))
        status = int(request.form.get('status'))
        
        # Update the product
        update_product_listing(
            seller_email, listing_id, product_title, product_name,
            product_description, quantity, product_price, status
        )
        
        flash(f'Product "{product_name}" updated successfully')
        return redirect(url_for('seller_products'))
    
    # GET request - show the form with product data
    # Get all categories for the dropdown
    categories = get_all_categories()
    
    return render_template('seller_product_form.html', 
                          categories=categories, 
                          product=product,
                          form_action=url_for('edit_product', listing_id=listing_id),
                          form_title='Edit Product')

@app.route('/seller/product/delete/<int:listing_id>', methods=['POST'])
def delete_product(listing_id):
    """Delete a product listing (set inactive)."""
    # Check if user is logged in and is a seller
    if 'email' not in session:
        flash('Please log in to delete a product')
        return redirect(url_for('login'))
    
    if not session.get('is_seller', False):
        flash('Only sellers can delete products')
        return redirect(url_for('home'))
    
    seller_email = session['email']
    
    # Delete the product (set inactive)
    delete_product_listing(seller_email, listing_id)
    
    flash('Product deleted successfully')
    return redirect(url_for('seller_products'))

# Order Routes
@app.route('/buyer/orders')
def buyers_orders():
    """Display all orders placed by the buyer."""
    # Check if user is logged in and is a buyer
    if 'email' not in session:
        flash('Please log in to view your orders')
        return redirect(url_for('login'))
    
    if not session.get('is_buyer', False):
        flash('Only buyers can access this page')
        return redirect(url_for('home'))
    
    # Get all orders for the buyer
    buyer_email = session['email']
    orders = get_buyer_orders(buyer_email)
    
    return render_template('buyers_order.html', orders=orders)

#order management
@app.route('/order_review')
def order_review():
    listing_id = request.args.get('listing_id', type=int)
    quantity = request.args.get('quantity', type=int)
    conn = get_db_connection()
    product = conn.execute(
        "SELECT * FROM Product_Listings WHERE listing_id = ?",
        (listing_id,)).fetchone()
    seller = conn.execute(
        "SELECT * FROM Sellers WHERE email = ?",
        (product['seller_email'],)
    ).fetchone()
    total = product['product_price'] * quantity
    reviews = get_product_reviews(seller['email'], listing_id)
    avg_rating = 0
    if reviews:
        avg_rating = sum(review['rating'] for review in reviews) / len(reviews)
    return render_template(
        'order_review.html',
        product=product,
        seller=seller,
        avg_rating = avg_rating,
        quantity=quantity,
        total=total)

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    listing_id = request.args.get('listing_id', type=int)
    quantity   = request.args.get('quantity',   type=int)
    conn = get_db_connection()
    product = conn.execute(
        "SELECT * FROM Product_Listings WHERE listing_id = ?",
        (listing_id,)
    ).fetchone()
    total = product['product_price'] * quantity
    buyer_email = session.get('email')
    saved_cards = conn.execute(
        "SELECT * FROM Credit_Cards WHERE Owner_email = ?",
        (buyer_email,)).fetchall()
    if request.method == 'POST':
        card_choice = request.form.get('card_choice')
        if card_choice == 'new':
            card_num = request.form['card_number']
            card_type = request.form['card_type']
            expire_month = request.form['exp_month']
            expire_year = request.form['exp_year']
            security_code = request.form['security_code']
            save_card = request.form.get('save_card') == 'yes'
            if save_card:
                conn.execute(
                    '''INSERT INTO Credit_Cards
                       (credit_card_num, card_type,
                        expire_month, expire_year,
                        security_code, Owner_email)
                       VALUES (?, ?, ?, ?, ?, ?)''',
                    (card_num,card_type, expire_month,expire_year,security_code,buyer_email))
                conn.commit()
                print("card saved")
            else:
                print("card not saved")

        order_id = create_order(
            seller_email=product['seller_email'],
            listing_id=listing_id,
            buyer_email=buyer_email,
            quantity=quantity,
            payment=total,
            date=datetime.now().strftime('%Y-%m-%d'))
        return redirect(url_for('order_confirmation', order_id=order_id))
    return render_template(
        'checkout.html',
        product=product,
        quantity=quantity,
        total=total,
        saved_cards=saved_cards)

@app.route('/order_confirmation')
def order_confirmation():
    order_id = request.args.get('order_id', type=int)
    conn = get_db_connection()
    order = conn.execute(
        "SELECT * FROM Orders WHERE order_id = ?",
        (order_id,)).fetchone()
    product = conn.execute(
        "SELECT product_name FROM Product_Listings WHERE listing_id = ?",
        (order['listing_id'],)).fetchone()
    seller = conn.execute(
        "SELECT business_name FROM Sellers WHERE email = ?",
        (order['seller_email'],)).fetchone()
    conn.close()
    return render_template(
        'order_confirmation.html',
        order=order,
        product=product,
        seller=seller)
@app.route('/seller/orders')
def sellers_orders():
    """Display all orders for products sold by the seller."""
    # Check if user is logged in and is a seller
    if 'email' not in session:
        flash('Please log in to view your orders')
        return redirect(url_for('login'))
    
    if not session.get('is_seller', False):
        flash('Only sellers can access this page')
        return redirect(url_for('home'))
    
    # Get all orders for the seller
    seller_email = session['email']
    orders = get_seller_orders(seller_email)
    
    return render_template('sellers_orders.html', orders=orders)

@app.route('/order/<int:order_id>')
def order_detail(order_id):
    """Display details of a specific order."""
    # Check if user is logged in
    if 'email' not in session:
        flash('Please log in to view order details')
        return redirect(url_for('login'))
    
    # Get the order details
    order = get_order_details(order_id)
    if not order:
        flash('Order not found')
        return redirect(url_for('home'))
    
    # Check authorization - only the buyer or seller of this order can view it
    user_email = session['email']
    if user_email != order['buyer_email'] and user_email != order['seller_email']:
        flash('You do not have permission to view this order')
        return redirect(url_for('home'))
    
    # For buyers, check if they've already reviewed this order
    has_review = False
    if session.get('is_buyer') and user_email == order['buyer_email']:
        conn = get_db_connection()
        cursor = conn.execute('SELECT * FROM Reviews WHERE order_id = ?', (order_id,))
        review = cursor.fetchone()
        conn.close()
        has_review = review is not None
    
    return render_template('order_detail.html', 
                          order=order, 
                          is_buyer=session.get('is_buyer'),
                          has_review=has_review)

@app.route('/order/<int:order_id>/review', methods=['GET', 'POST'])
def review_order(order_id):
    """Create or edit a review for an order."""
    # Check if user is logged in and is a buyer
    if 'email' not in session:
        flash('Please log in to review an order')
        return redirect(url_for('login'))
    
    if not session.get('is_buyer', False):
        flash('Only buyers can review orders')
        return redirect(url_for('home'))
    
    # Get the order details
    order = get_order_details(order_id)
    if not order:
        flash('Order not found')
        return redirect(url_for('buyer_orders'))
    
    # Check if this is the buyer's order
    buyer_email = session['email']
    if buyer_email != order['buyer_email']:
        flash('You can only review your own orders')
        return redirect(url_for('buyer_orders'))
    
    # Handle form submission
    if request.method == 'POST':
        review_text = request.form.get('review_text')
        rating = int(request.form.get('rating'))
        
        # Create or update the review
        create_product_review(order_id, review_text, rating)
        
        flash('Review submitted successfully')
        return redirect(url_for('order_detail', order_id=order_id))
    
    # GET request - show the form
    # Check if there's an existing review
    conn = get_db_connection()
    cursor = conn.execute('SELECT * FROM Reviews WHERE order_id = ?', (order_id,))
    review = cursor.fetchone()
    conn.close()
    
    return render_template('review_form.html', 
                          order=order,
                          review=review,
                          form_action=url_for('review_order', order_id=order_id))

# Extra Credit: Shopping Cart
# Shopping Cart Routes
@app.route('/cart')
def cart():
    """Display the buyer's shopping cart."""
    # Check if user is logged in and is a buyer
    if 'email' not in session:
        flash('Please log in to view your cart')
        return redirect(url_for('login'))
    
    if not session.get('is_buyer', False):
        flash('Only buyers can access the shopping cart')
        return redirect(url_for('home'))
    
    # Get the cart items
    buyer_email = session['email']
    cart_items = get_cart_items(buyer_email)
    
    # Calculate total
    total = sum(item['product_price'] * item['quantity'] for item in cart_items)
    
    return render_template('cart.html', 
                          cart_items=cart_items,
                          total=total)

@app.route('/cart/add', methods=['POST'])
def add_to_cart_route():
    """Add an item to the shopping cart."""
    # Check if user is logged in and is a buyer
    if 'email' not in session:
        flash('Please log in to add items to your cart')
        return redirect(url_for('login'))
    
    if not session.get('is_buyer', False):
        flash('Only buyers can add items to the shopping cart')
        return redirect(url_for('home'))
    
    # Get form data
    seller_email = request.form.get('seller_email')
    listing_id = int(request.form.get('listing_id'))
    quantity = int(request.form.get('quantity', 1))
    
    # Add to cart
    buyer_email = session['email']
    add_to_cart(buyer_email, seller_email, listing_id, quantity)
    
    flash('Item added to cart successfully')
    
    # Redirect to appropriate page
    redirect_to = request.form.get('redirect_to', 'cart')
    if redirect_to == 'product':
        return redirect(url_for('product_detail', seller_email=seller_email, listing_id=listing_id))
    else:
        return redirect(url_for('cart'))

@app.route('/cart/update', methods=['POST'])
def update_cart():
    """Update the quantity of an item in the shopping cart."""
    # Check if user is logged in and is a buyer
    if 'email' not in session:
        flash('Please log in to update your cart')
        return redirect(url_for('login'))
    
    if not session.get('is_buyer', False):
        flash('Only buyers can update the shopping cart')
        return redirect(url_for('home'))
    
    # Get form data
    seller_email = request.form.get('seller_email')
    listing_id = int(request.form.get('listing_id'))
    quantity = int(request.form.get('quantity'))
    
    # Update cart
    buyer_email = session['email']
    update_cart_quantity(buyer_email, seller_email, listing_id, quantity)
    
    flash('Cart updated successfully')
    return redirect(url_for('cart'))

@app.route('/cart/remove', methods=['POST'])
def remove_from_cart_route():
    """Remove an item from the shopping cart."""
    # Check if user is logged in and is a buyer
    if 'email' not in session:
        flash('Please log in to remove items from your cart')
        return redirect(url_for('login'))
    
    if not session.get('is_buyer', False):
        flash('Only buyers can remove items from the shopping cart')
        return redirect(url_for('home'))
    
    # Get form data
    seller_email = request.form.get('seller_email')
    listing_id = int(request.form.get('listing_id'))
    
    # Remove from cart
    buyer_email = session['email']
    remove_from_cart(buyer_email, seller_email, listing_id)
    
    flash('Item removed from cart successfully')
    return redirect(url_for('cart'))

@app.route('/cart/clear', methods=['POST'])
def clear_cart_route():
    """Clear all items from the shopping cart."""
    # Check if user is logged in and is a buyer
    if 'email' not in session:
        flash('Please log in to clear your cart')
        return redirect(url_for('login'))
    
    if not session.get('is_buyer', False):
        flash('Only buyers can clear the shopping cart')
        return redirect(url_for('home'))
    
    # Clear cart
    buyer_email = session['email']
    clear_cart(buyer_email)
    
    flash('Cart cleared successfully')
    return redirect(url_for('cart'))
@app.route('/cart/checkout_cart', methods=['GET', 'POST'])
def checkout_cart():
    """Checkout process - review items and payment methods."""
    # Check if user is logged in and is a buyer
    if 'email' not in session:
        flash('Please log in to checkout')
        return redirect(url_for('login'))
    
    if not session.get('is_buyer', False):
        flash('Only buyers can checkout')
        return redirect(url_for('home'))
    
    buyer_email = session['email']
    
    # Handle form submission
    if request.method == 'POST':
        try:
            # Perform checkout
            orders = checkout_cart(buyer_email)
            
            if not orders:
                flash('Your cart is empty')
                return redirect(url_for('cart'))
            
            flash('Checkout completed successfully! Orders have been created.')
            return redirect(url_for('buyer_orders'))
            
        except ValueError as e:
            flash(str(e))
            return redirect(url_for('checkout_cart'))
    
    # GET request - show checkout page
    # Get cart items
    cart_items = get_cart_items(buyer_email)
    
    if not cart_items:
        flash('Your cart is empty')
        return redirect(url_for('cart'))
    
    # Calculate total
    total = sum(item['product_price'] * item['quantity'] for item in cart_items)
    
    # Get payment methods
    credit_cards = get_credit_cards(buyer_email)
    
    return render_template('checkout_cart.html',
                           cart_items=cart_items,
                           total=total,
                           credit_cards=credit_cards)

def get_wishlist_items(buyer_email):
    """Get all items in a buyer's wishlist."""
    conn = get_db_connection()
    
    # Check if wishlist table exists, create if not
    conn.execute('''
    CREATE TABLE IF NOT EXISTS Wishlist (
        buyer_email TEXT,
        seller_email TEXT,
        listing_id INTEGER,
        date_added TEXT,
        PRIMARY KEY (buyer_email, seller_email, listing_id),
        FOREIGN KEY (buyer_email) REFERENCES Buyers(email),
        FOREIGN KEY (seller_email, listing_id) REFERENCES Product_Listings(seller_email, listing_id)
    )
    ''')
    
    cursor = conn.execute('''
    SELECT w.seller_email, w.listing_id, w.date_added,
           p.product_name, p.product_price, p.quantity, p.status,
           s.business_name as seller_name
    FROM Wishlist w
    JOIN Product_Listings p ON w.seller_email = p.seller_email AND w.listing_id = p.listing_id
    JOIN Sellers s ON w.seller_email = s.email
    WHERE w.buyer_email = ?
    ORDER BY w.date_added DESC
    ''', (buyer_email,))
    
    result = cursor.fetchall()
    conn.close()
    return result

def add_to_wishlist(buyer_email, seller_email, listing_id):
    """Add an item to the wishlist."""
    conn = get_db_connection()
    
    # Check if wishlist table exists, create if not
    conn.execute('''
    CREATE TABLE IF NOT EXISTS Wishlist (
        buyer_email TEXT,
        seller_email TEXT,
        listing_id INTEGER,
        date_added TEXT,
        PRIMARY KEY (buyer_email, seller_email, listing_id),
        FOREIGN KEY (buyer_email) REFERENCES Buyers(email),
        FOREIGN KEY (seller_email, listing_id) REFERENCES Product_Listings(seller_email, listing_id)
    )
    ''')
    
    # Check if the item is already in the wishlist
    cursor = conn.execute('''
    SELECT 1
    FROM Wishlist
    WHERE buyer_email = ? AND seller_email = ? AND listing_id = ?
    ''', (buyer_email, seller_email, listing_id))
    
    if cursor.fetchone():
        conn.close()
        return False
    
    # Add to wishlist with current date
    current_date = datetime.now().strftime('%Y-%m-%d')
    conn.execute('''
    INSERT INTO Wishlist (buyer_email, seller_email, listing_id, date_added)
    VALUES (?, ?, ?, ?)
    ''', (buyer_email, seller_email, listing_id, current_date))
    
    conn.commit()
    conn.close()
    return True

def remove_from_wishlist(buyer_email, seller_email, listing_id):
    """Remove an item from the wishlist."""
    conn = get_db_connection()
    conn.execute('''
    DELETE FROM Wishlist
    WHERE buyer_email = ? AND seller_email = ? AND listing_id = ?
    ''', (buyer_email, seller_email, listing_id))
    conn.commit()
    conn.close()

@app.route('/wishlist')
def view_wishlist():
    """Display the buyer's wishlist."""
    # Check if user is logged in and is a buyer
    if 'email' not in session:
        flash('Please log in to view your wishlist')
        return redirect(url_for('login'))
    
    if not session.get('is_buyer', False):
        flash('Only buyers can access the wishlist')
        return redirect(url_for('home'))
    
    # Get the wishlist items
    buyer_email = session['email']
    wishlist_items = get_wishlist_items(buyer_email)
    
    return render_template('wishlist.html', wishlist_items=wishlist_items)

@app.route('/wishlist/add', methods=['POST'])
def add_to_wishlist_route():
    """Add an item to the wishlist."""
    # Check if user is logged in and is a buyer
    if 'email' not in session:
        flash('Please log in to add items to your wishlist')
        return redirect(url_for('login'))
    
    if not session.get('is_buyer', False):
        flash('Only buyers can add items to the wishlist')
        return redirect(url_for('home'))
    
    # Get form data
    seller_email = request.form.get('seller_email')
    listing_id = int(request.form.get('listing_id'))
    
    # Add to wishlist
    buyer_email = session['email']
    success = add_to_wishlist(buyer_email, seller_email, listing_id)
    
    if success:
        flash('Item added to wishlist successfully')
    else:
        flash('Item is already in your wishlist')
    
    # Redirect to appropriate page
    redirect_to = request.form.get('redirect_to', 'wishlist')
    if redirect_to == 'product':
        return redirect(url_for('product_detail', seller_email=seller_email, listing_id=listing_id))
    else:
        return redirect(url_for('view_wishlist'))

@app.route('/wishlist/remove', methods=['POST'])
def remove_from_wishlist_route():
    """Remove an item from the wishlist."""
    # Check if user is logged in and is a buyer
    if 'email' not in session:
        flash('Please log in to remove items from your wishlist')
        return redirect(url_for('login'))
    
    if not session.get('is_buyer', False):
        flash('Only buyers can remove items from the wishlist')
        return redirect(url_for('home'))
    
    # Get form data
    seller_email = request.form.get('seller_email')
    listing_id = int(request.form.get('listing_id'))
    
    # Remove from wishlist
    buyer_email = session['email']
    remove_from_wishlist(buyer_email, seller_email, listing_id)
    
    flash('Item removed from wishlist successfully')
    return redirect(url_for('view_wishlist'))

@app.route('/wishlist/add_all_to_cart', methods=['POST'])
def add_wishlist_to_cart():
    """Add all wishlist items to the cart."""
    # Check if user is logged in and is a buyer
    if 'email' not in session:
        flash('Please log in to add items to your cart')
        return redirect(url_for('login'))
    
    if not session.get('is_buyer', False):
        flash('Only buyers can add items to the cart')
        return redirect(url_for('home'))
    
    # Get the wishlist items
    buyer_email = session['email']
    wishlist_items = get_wishlist_items(buyer_email)
    
    # Add each item to the cart
    for item in wishlist_items:
        if item['status'] == 1 and item['quantity'] > 0:
            add_to_cart(buyer_email, item['seller_email'], item['listing_id'], 1)
    
    flash('Wishlist items added to cart successfully')
    return redirect(url_for('cart'))

# Helper functions for HelpDesk Support
def get_helpdesk_requests():
    """Get all support requests from the database."""
    conn = get_db_connection()
    cursor = conn.execute('''
        SELECT *
        FROM Requests
        ORDER BY request_id DESC
    ''')
    requests = cursor.fetchall()
    conn.close()
    return requests

def submit_helpdesk_request(sender_email, request_type, request_desc):
    """Create a new support request."""
    conn = get_db_connection()
    cursor = conn.execute("SELECT MAX(request_id) as max_id FROM Requests")
    result = cursor.fetchone()
    request_id = 1 if result is None or result['max_id'] is None else result['max_id'] + 1
    helpdesk_staff_email = 'helpdeskteam@nittybiz.com'
    request_status = 0
    conn.execute('''
        INSERT INTO Requests (request_id, sender_email, helpdesk_staff_email, request_type, request_desc, request_status)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (request_id, sender_email, helpdesk_staff_email, request_type, request_desc, request_status))
    conn.commit()
    conn.close()
    return request_id

def claim_helpdesk_request(request_id, staff_email):
    """Claim an unassigned support request."""
    conn = get_db_connection()
    conn.execute('''
        UPDATE Requests
        SET helpdesk_staff_email = ?
        WHERE request_id = ?
    ''', (staff_email, request_id))
    conn.commit()
    conn.close()

def complete_helpdesk_request(request_id):
    """Mark a support request as completed."""
    conn = get_db_connection()
    conn.execute('''
        UPDATE Requests
        SET request_status = 1
        WHERE request_id = ?
    ''', (request_id,))
    conn.commit()
    conn.close()

def extract_category_info(request_desc):
    """Extract category name and parent category from request description."""
    # Look for the pattern where category info is at the end of the description
    if '\n\nCategory Name: ' in request_desc:
        lines = request_desc.split('\n\n')[-1].split('\n')
        category_name = lines[0].replace('Category Name: ', '')
        parent_category = lines[1].replace('Parent Category: ', '')
        return category_name, parent_category
    return None, None

def add_category_from_request(category_name, parent_category):
    """Add a new category from a request."""
    conn = get_db_connection()
    
    # Check if category already exists
    cursor = conn.execute('SELECT * FROM Categories WHERE category_name = ?', (category_name,))
    if cursor.fetchone():
        conn.close()
        return False, "Category already exists"
    
    # Check if parent category exists (unless it's 'All')
    if parent_category != 'All':
        cursor = conn.execute('SELECT * FROM Categories WHERE category_name = ?', (parent_category,))
        if not cursor.fetchone():
            conn.close()
            return False, "Parent category doesn't exist"
    
    # Add the category
    conn.execute('''
        INSERT INTO Categories (category_name, parent_category)
        VALUES (?, ?)
    ''', (category_name, parent_category))
    
    conn.commit()
    conn.close()
    return True, "Category added successfully"

# Extra Credit: Helpdesk Support
# Routes for HelpDesk Support
@app.route('/submit_request', methods=['GET', 'POST'])
def submit_request():
    """Handle support request submission."""
    # Check if user is logged in
    if 'email' not in session:
        flash('Please log in to submit a support request', 'error')
        return redirect(url_for('login'))
    
    # Only buyers and sellers can submit requests
    if not (session.get('is_buyer') or session.get('is_seller')):
        flash('Only buyers and sellers can submit support requests', 'error')
        return redirect(url_for('home'))
    
    # Get all categories for the dropdown (for new category requests)
    conn = get_db_connection()
    cursor = conn.execute('SELECT * FROM Categories ORDER BY category_name')
    categories = cursor.fetchall()
    conn.close()
    
    if request.method == 'POST':
        # Get form data
        request_type = request.form.get('request_type')
        request_desc = request.form.get('request_desc')
        
        # For new category requests, add category details to the description
        if request_type == 'new_category':
            category_name = request.form.get('category_name')
            parent_category = request.form.get('parent_category')
            
            if not category_name:
                flash('Please enter a name for the new category', 'error')
                return render_template('submit_request.html', categories=categories)
            
            # Add category details to the description
            request_desc += f"\n\nCategory Name: {category_name}\nParent Category: {parent_category}"
        
        # Submit the request
        sender_email = session['email']
        submit_helpdesk_request(sender_email, request_type, request_desc)
        
        flash('Your support request has been submitted successfully', 'success')
        return redirect(url_for('home'))
    
    # GET request - show the form
    return render_template('submit_request.html', categories=categories)

@app.route('/helpdesk/requests')
def helpdesk_requests():
    """Display helpdesk support requests for management."""
    # Check if user is logged in and is a helpdesk staff
    if 'email' not in session:
        flash('Please log in to access this page', 'error')
        return redirect(url_for('login'))
    
    if not session.get('is_helpdesk'):
        flash('Only helpdesk staff can access this page', 'error')
        return redirect(url_for('home'))
    
    # Get all requests
    requests = get_helpdesk_requests()
    
    return render_template('helpdesk_requests.html', requests=requests)

@app.route('/helpdesk/claim_request/<int:request_id>', methods=['POST'])
def claim_request(request_id):
    """Handle request claiming by helpdesk staff."""
    # Check if user is logged in and is a helpdesk staff
    if 'email' not in session:
        flash('Please log in to access this feature', 'error')
        return redirect(url_for('login'))
    
    if not session.get('is_helpdesk'):
        flash('Only helpdesk staff can claim requests', 'error')
        return redirect(url_for('home'))
    
    # Claim the request
    claim_helpdesk_request(request_id, session['email'])
    
    flash('Request claimed successfully', 'success')
    return redirect(url_for('helpdesk_requests'))

@app.route('/helpdesk/complete_request/<int:request_id>', methods=['POST'])
def complete_request(request_id):
    """Handle request completion by helpdesk staff."""
    # Check if user is logged in and is a helpdesk staff
    if 'email' not in session:
        flash('Please log in to access this feature', 'error')
        return redirect(url_for('login'))
    
    if not session.get('is_helpdesk'):
        flash('Only helpdesk staff can complete requests', 'error')
        return redirect(url_for('home'))
    
    # Complete the request
    complete_helpdesk_request(request_id)
    
    flash('Request marked as completed', 'success')
    return redirect(url_for('helpdesk_requests'))

@app.route('/helpdesk/add_new_category/<int:request_id>', methods=['POST'])
def add_new_category(request_id):
    """Handle adding a new category from a request."""
    # Check if user is logged in and is a helpdesk staff
    if 'email' not in session:
        flash('Please log in to access this feature', 'error')
        return redirect(url_for('login'))
    
    if not session.get('is_helpdesk'):
        flash('Only helpdesk staff can add categories', 'error')
        return redirect(url_for('home'))
    
    # Get category details from the form
    category_name = request.form.get('category_name')
    parent_category = request.form.get('parent_category')
    
    if not category_name:
        flash('Category name is required', 'error')
        return redirect(url_for('helpdesk_requests'))
    
    # Add the new category
    success, message = add_category_from_request(category_name, parent_category)
    
    if success:
        # Mark the request as completed
        complete_helpdesk_request(request_id)
        flash(f'New category "{category_name}" added successfully', 'success')
    else:
        flash(f'Error adding category: {message}', 'error')
    
    return redirect(url_for('helpdesk_requests'))

# Update to the home route to include helpdesk statistics
def update_home_route():
    if session.get('is_helpdesk'):
        requests = get_helpdesk_requests()
        unassigned_count = 0
        assigned_count = 0
        completed_count = 0
        for req in requests:
            if req['request_status'] == 0 and req['helpdesk_staff_email'] == 'helpdeskteam@nittybiz.com':
                unassigned_count += 1
            elif req['request_status'] == 0 and req['helpdesk_staff_email'] == session['email']:
                assigned_count += 1
            elif req['request_status'] == 1:
                completed_count += 1
        return render_template('home_helpdesk.html',
                              unassigned_count=unassigned_count,
                              assigned_count=assigned_count,
                              completed_count=completed_count)
@app.route('/home')
def home():
    if 'email' not in session:
        flash('Please log in to access the home page')
        return redirect(url_for('login'))
    
    if session.get('is_buyer'):
        return render_template('home_buyer.html')
    elif session.get('is_seller'):
        return render_template('home_seller.html')
    elif session.get('is_helpdesk'):
        requests = get_helpdesk_requests()
        unassigned_count = 0
        assigned_count = 0
        completed_count = 0
        for req in requests:
            if req['request_status'] == 0 and req['helpdesk_staff_email'] == 'helpdeskteam@nittybiz.com':
                unassigned_count += 1
            elif req['request_status'] == 0 and req['helpdesk_staff_email'] == session['email']:
                assigned_count += 1
            elif req['request_status'] == 1:
                completed_count += 1
        return render_template('home_helpdesk.html',
                              unassigned_count=unassigned_count,
                              assigned_count=assigned_count,
                              completed_count=completed_count)
    else:
        flash('Invalid user type')
        return redirect(url_for('logout'))

if __name__ == "__main__":
    app.run(debug=True)
