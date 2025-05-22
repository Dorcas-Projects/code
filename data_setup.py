import csv
import hashlib
import sqlite3

#helper function to sha256 hash a password
def sha256hash(password):
    hashed_pw =  hashlib.sha256(password.encode()).hexdigest()
    return hashed_pw

#set up the user table in the database by importing data from users csv file and then inserting into database tables
def setup():
    #Connect to (or create) the SQLite database
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    #Create Users table
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS Users (
                   email TEXT PRIMARY KEY NOT NULL,
                   password TEXT NOT NULL)
                   ''')

    #Create Helpdesk table
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS Helpdesk (
                   email TEXT PRIMARY KEY NOT NULL,
                   position TEXT)
                   ''')

    #Create Requests table
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS Requests (
                   request_id INTEGER PRIMARY KEY,
                   sender_email TEXT NOT NULL,
                   helpdesk_staff_email TEXT NOT NULL,
                   request_type TEXT,
                   request_desc TEXT,
                   request_status INTEGER CHECK(request_status IN (0, 1)),
                   FOREIGN KEY (sender_email) REFERENCES Users(email),
                   FOREIGN KEY (helpdesk_staff_email) REFERENCES Helpdesk(email))
                   ''')
    #Create Addresses table
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS Addresses (
                   address_id TEXT PRIMARY KEY,
                   zipcode TEXT,
                   street_num TEXT,
                   street_name TEXT)
                   ''')
    #Create Zipcode Info table
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS Zipcode_Info (
                   zipcode TEXT PRIMARY KEY,
                   city TEXT,
                   state TEXT)
                   ''')
    #Create Buyers table
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS Buyers (
                    email TEXT PRIMARY KEY NOT NULL,
                   business_name TEXT,
                   buyer_address_id INTEGER,
                   FOREIGN KEY (email) REFERENCES Users(email),
                   FOREIGN KEY (buyer_address_id) REFERENCES Addresses(address_id))
                   ''')
    #Create Credit Cards Table
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS Credit_Cards (
                   credit_card_num TEXT PRIMARY KEY,
                   card_type TEXT,
                   expire_month INTEGER,
                   expire_year INTEGER,
                   security_code TEXT,
                   Owner_email TEXT,
                   FOREIGN KEY (Owner_email) REFERENCES Buyer(email))
                   ''')
    #Create Sellers table
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS Sellers (
                   email TEXT PRIMARY KEY NOT NULL,
                   business_name TEXT,
                   business_address_id INTEGER,
                   bank_routing_number TEXT,
                   bank_account_number TEXT,
                   balance REAL,
                   FOREIGN KEY (email) REFERENCES Users(email),
                   FOREIGN KEY (business_address_id) REFERENCES Addresses(address_id))
                   ''')
    #Create Categories table
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS Categories (
                   parent_category TEXT,
                   category_name TEX T PRIMARY KEY,
                   FOREIGN KEY (parent_category) REFERENCES Categories(category_name))
                   ''')
    #Create Product Listings table
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS Product_Listings (
                   seller_email TEXT NOT NULL,
                   listing_id INTEGER,
                   category TEXT,
                   product_title TEXT,
                   product_name TEXT,
                   product_description TEXT,
                   quantity INTEGER,
                   product_price REAL,
                   status INTEGER DEFAULT 1 CHECK(status IN (0, 1, 2)),
                   PRIMARY KEY (seller_email, listing_id),
                   FOREIGN KEY (seller_email) REFERENCES Sellers(email),
                   FOREIGN KEY (category) REFERENCES Categories(category_name))
                   ''')
    #Create Orders table
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS Orders (
                   order_id INTEGER PRIMARY KEY,
                   seller_email TEXT NOT NULL,
                   listing_id INTEGER,
                   buyer_email TEXT NOT NULL,
                   date TEXT,
                   quantity INTEGER,
                   payment REAL,
                   foreign key (seller_email, listing_id) REFERENCES Product_Listings(seller_email, listing_id),
                   FOREIGN KEY (buyer_email) REFERENCES Buyers(email))
                   ''')
    #Create Reviews Table
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS Reviews (
                   order_id INTEGER PRIMARY KEY,
                   review_desc TEXT,
                   rating INTEGER,
                   FOREIGN KEY (order_id) REFERENCES Orders(order_id))
                   ''')

    #Insert Data into Users table from CSV file
    with open('CSV Files/Users.csv', 'r') as file:
        reader = csv.reader(file)
        next(reader) #skip the first row that contains column headers
        for row in reader:
            email = row[0]
            hashed_password = sha256hash(row[1]) #hash the password which is the second element of each row
            cursor.execute('INSERT INTO USERS VALUES (?, ?)', (email, hashed_password))#insert into the USERS table

    #Insert Data into Helpdesk table from CSV file
    with open('CSV Files/Helpdesk.csv', 'r') as file:
        reader = csv.reader(file)
        next(reader) #skip the first row that contains column headers
        for row in reader:
            email = row[0]
            position = row[1]
            cursor.execute('INSERT INTO Helpdesk VALUES (?, ?)', (email, position))#insert into the Helpdesk table

    #Insert Data into Requests table from CSV file
    with open('CSV Files/Requests.csv', 'r') as file:
        reader = csv.reader(file)
        next(reader) #skip the first row that contains column headers
        for row in reader:
            request_id = row[0]
            sender_email = row[1]
            helpdesk_staff_email = row[2]
            request_type = row[3]
            request_desc = row[4]
            request_status = row[5]
            cursor.execute('INSERT INTO Requests VALUES (?, ?, ?, ?, ?, ?)', (request_id, sender_email, helpdesk_staff_email, request_type, request_desc, request_status))#insert into the Requests table

    #Insert Data into Addresses table from CSV file
    with open('CSV Files/Address.csv', 'r') as file:
        reader = csv.reader(file)
        next(reader) #skip the first row that contains column headers
        for row in reader:
            address_id = row[0]
            zipcode = row[1]
            street_num = row[2]
            street_name = row[3]
            cursor.execute('INSERT INTO Addresses VALUES (?, ?, ?, ?)', (address_id, zipcode, street_num, street_name))#insert into the Addresses table

    #Insert Data into Zipcode Info table from CSV file
    with open('CSV Files/Zipcode_Info.csv', 'r') as file:
        reader = csv.reader(file)
        next(reader) #skip the first row that contains column headers
        for row in reader:
            zipcode = row[0]
            city = row[1]
            state = row[2]
            cursor.execute('INSERT INTO Zipcode_Info VALUES (?, ?, ?)', (zipcode, city, state))#insert into the Zipcode Info table

    #Insert Data into Buyers table from CSV file
    with open('CSV Files/Buyers.csv', 'r') as file:
        reader = csv.reader(file)
        next(reader) #skip the first row that contains column headers
        for row in reader:
            email = row[0]
            business_name = row[1]
            buyer_address_id = row[2]
            cursor.execute('INSERT INTO Buyers VALUES (?, ?, ?)', (email, business_name, buyer_address_id))#insert into the Buyers table

    #Insert Data into Credit Cards table from CSV file
    with open('CSV Files/Credit_Cards.csv', 'r') as file:
        reader = csv.reader(file)
        next(reader) #skip the first row that contains column headers
        for row in reader:
            credit_card_num = row[0]
            card_type = row[1]
            expire_month = row[2]
            expire_year = row[3]
            security_code = row[4]
            owner_email = row[5]
            cursor.execute('INSERT INTO Credit_Cards VALUES (?, ?, ?, ?, ?, ?)', (credit_card_num, card_type, expire_month, expire_year, security_code, owner_email))#insert into the Credit Cards table

    #Insert Data into Sellers table from CSV file
    with open('CSV Files/Sellers.csv', 'r') as file:
        reader = csv.reader(file)
        next(reader) #skip the first row that contains column headers
        for row in reader:
            email = row[0]
            business_name = row[1]
            business_address_id = row[2]
            bank_routing_number = row[3]
            bank_account_number = row[4]
            balance = row[5]
            cursor.execute('INSERT INTO Sellers VALUES (?, ?, ?, ?, ?, ?)', (email, business_name, business_address_id, bank_routing_number, bank_account_number, balance))#insert into the Sellers table

    #Insert Data into Categories table from CSV file
    with open('CSV Files/Categories.csv', 'r') as file:
        reader = csv.reader(file)
        next(reader) #skip the first row that contains column headers
        for row in reader:
            parent_category = row[0]
            category_name = row[1]
            cursor.execute('INSERT INTO Categories VALUES (?, ?)', (parent_category, category_name))#insert into the Categories table

    #Insert Data into Product Listings table from CSV file
    with open('CSV Files/Product_Listings.csv', 'r') as file:
        reader = csv.reader(file)
        next(reader) #skip the first row that contains column headers
        for row in reader:
            seller_email = row[0]
            listing_id = row[1]
            category = row[2]
            product_title = row[3]
            product_name = row[4]
            product_description = row[5]
            quantity = row[6]
            price =  row[7].replace("$", "").replace(",", "").strip() #remove $ and , from price
            product_price = float(price)
            status = row[8]
            cursor.execute('INSERT INTO Product_Listings VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', (seller_email, listing_id, category, product_title, product_name, product_description, quantity, product_price, status))#insert into the Product Listings table

    #Insert Data into Orders table from CSV file
    with open('CSV Files/Orders.csv', 'r') as file:
        reader = csv.reader(file)
        next(reader) #skip the first row that contains column headers
        for row in reader:
            order_id = row[0]
            seller_email = row[1]
            listing_id = row[2]
            buyer_email = row[3]
            date = row[4]
            quantity = row[5]
            payment = row[6]
            cursor.execute('INSERT INTO Orders VALUES (?, ?, ?, ?, ?, ?, ?)', (order_id, seller_email, listing_id, buyer_email, date, quantity, payment))#insert into the Orders table

    #Insert Data into Reviews table from CSV file
    with open('CSV Files/Reviews.csv', 'r') as file:
        reader = csv.reader(file)
        next(reader) #skip the first row that contains column headers
        for row in reader:
            order_id = row[0]
            rating = row[1]
            review_desc = row[2]
            cursor.execute('INSERT INTO Reviews VALUES (?, ?, ?)', (order_id, review_desc, rating))#insert into the Reviews table

    print("Data Inserted")
    # Commit the transaction and close the connection
    connection.commit()
    connection.close()

#testing: drop all tables if needed
def drop_all_tables():
    # Connect to the SQLite database
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()

    # Query to get all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    # Drop each table
    for table_name in tables:
        cursor.execute(f"DROP TABLE IF EXISTS {table_name[0]};")
        print(f"Dropped table: {table_name[0]}")

    # Commit changes and close connection
    connection.commit()
    connection.close()

#clear tables before inserting data
drop_all_tables()
setup()
