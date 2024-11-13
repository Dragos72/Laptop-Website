from flask import Flask, jsonify, render_template, url_for, request
import pypyodbc as odbc

app = Flask(__name__)

DRIVER_NAME = 'SQL SERVER'
SERVER_NAME = 'DESKTOP-NEGON5B\SQLEXPRESS'
DATABASE_NAME = 'Website_Database'

connection_string = f"""
    DRIVER={{{DRIVER_NAME}}};
    SERVER={SERVER_NAME};
    DATABASE={DATABASE_NAME};
    Trust_Connection=yes;
"""
'''
conn = odbc.connect(connection_string)
print(conn)
'''

# Connect to the database
try:
    conn = odbc.connect(connection_string)
    print("Connection successful!")
except Exception as e:
    print(f"Error: {e}")

# SQL query to get the schema of the 'Users' table
query = """
SELECT 
    COLUMN_NAME,
    DATA_TYPE,
    CHARACTER_MAXIMUM_LENGTH,
    IS_NULLABLE
FROM 
    INFORMATION_SCHEMA.COLUMNS
WHERE 
    TABLE_NAME = 'Users';
"""

'''
# Execute the query and print the results
try:
    cursor = conn.cursor()
    cursor.execute(query)
    schema = cursor.fetchall()
    
    print("Schema of 'Users' table:")
    for column in schema:
        column_name, data_type, max_length, is_nullable = column
        print(f"Column: {column_name}, Data Type: {data_type}, Max Length: {max_length}, Nullable: {is_nullable}")

    # Close the cursor and connection
    cursor.close()
    conn.close()
except Exception as e:
    print(f"Error: {e}")
'''


@app.route('/')
def login_page():
    return render_template('index.html')

'''
@app.route('/mainPage')
def main_page():
    return render_template('main_page.html')
'''

@app.route('/schema')
def get_schema():
    try:
        conn = odbc.connect(connection_string)
        query = """
        SELECT 
            COLUMN_NAME,
            DATA_TYPE,
            CHARACTER_MAXIMUM_LENGTH,
            IS_NULLABLE
        FROM 
            INFORMATION_SCHEMA.COLUMNS
        WHERE 
            TABLE_NAME = 'Users';
        """
        cursor = conn.cursor()
        cursor.execute(query)
        schema = cursor.fetchall()
        cursor.close()
        conn.close()

        # Print schema to the console (for debugging)
        print("Schema of 'Users' table:")
        for column in schema:
            print(f"Column: {column[0]}, Data Type: {column[1]}, Max Length: {column[2]}, Nullable: {column[3]}")

        # Convert schema data to a list of dictionaries for JSON response
        schema_data = [
            {
                "column_name": column[0],
                "data_type": column[1],
                "max_length": column[2],
                "is_nullable": column[3]
            }
            for column in schema
        ]
        return jsonify(schema_data)
    except Exception as e:
        return jsonify({"error": str(e)})
    


@app.route('/user_cart_data')
def get_user_cart_data():
    try:
        conn = odbc.connect(connection_string)
        query = """
        SELECT 
            u.UserID,
            u.FirstName,
            u.LastName,
            u.Email,
            u.PhoneNumber,
            u.UserType,
            s.CartID,
            s.CreationDate
        FROM 
            Users u
        JOIN 
            ShoppingCart s ON u.UserID = s.UserID;
        """
        cursor = conn.cursor()
        cursor.execute(query)
        user_cart_data = cursor.fetchall()
        cursor.close()
        conn.close()

        # Convert query result to a list of dictionaries for JSON response
        data = [
            {
                "UserID": row[0],
                "FirstName": row[1],
                "LastName": row[2],
                "Email": row[3],
                "PhoneNumber": row[4],
                "UserType": row[5],
                "CartID": row[6],
                "CreationDate": row[7]
            }
            for row in user_cart_data
        ]
        
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)})
    

from flask import render_template

@app.route('/welcome')
def welcome_user():
    email = 'alice.brown@example.com'
    
    try:
        conn = odbc.connect(connection_string)
        query = """
        SELECT 
            FirstName,
            LastName
        FROM 
            Users
        WHERE 
            Email = ?;
        """
        cursor = conn.cursor()
        cursor.execute(query, (email,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if result:
            first_name, last_name = result
            return render_template('welcome.html', first_name=first_name, last_name=last_name)
        else:
            return "User not found.", 404
    except Exception as e:
        return jsonify({"error": str(e)})


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    try:
        conn = odbc.connect(connection_string)
        query = """
        SELECT FirstName, LastName
        FROM Users
        WHERE Email = ? AND Password = ?;
        """
        cursor = conn.cursor()
        cursor.execute(query, (email, password))
        user = cursor.fetchone()
        #Close the database connection
        cursor.close()
        conn.close()

        if user:
            # Login successful, send a success response
            return jsonify({"success": True, "first_name": user[0], "last_name": user[1]})
        else:
            # Login failed, send a failure message
            return jsonify({"success": False, "message": "Invalid email or password."})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

### Create a New Account
@app.route('/create_account')
def create_account():
    return render_template('createUser.html')

@app.route('/catalog')
def catalog():
    # You may fetch categories and laptop data from your database here
    return render_template('catalog.html')

@app.route('/create_user', methods=['POST'])
def create_user():
    data = request.get_json()
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    email = data.get('email')
    password = data.get('password')
    phone_number = data.get('phone_number')

    #Verify that each element is not empty
    if not (first_name):
         return jsonify({"success": False, "message": "First name not completed."})
    
    if not (last_name):
         return jsonify({"success": False, "message": "Last name not completed."})

    if not (email):
         return jsonify({"success": False, "message": "Email not completed."})
    
    if not (password):
         return jsonify({"success": False, "message": "Password not completed."})

    #If all fields are completed, proceed with opening the connection to the database
    try:
        # Connect to the database
        conn = odbc.connect(connection_string)
        cursor = conn.cursor()

        # Check if email already exists
        email_check_query = "SELECT 1 FROM Users WHERE Email = ?;"
        cursor.execute(email_check_query, (email,))
        if cursor.fetchone():
            return jsonify({"success": False, "message": "Email already exists."})

        # Insert the new user
        insert_query = """
        INSERT INTO Users (FirstName, LastName, Email, Password, PhoneNumber)
        VALUES (?, ?, ?, ?, ?);
        """
        cursor.execute(insert_query, (
            first_name, last_name, email, password, phone_number
        ))
        conn.commit()

        #Close the database connection
        cursor.close()
        conn.close()

        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})
    
'''
@app.route('/get_categories', methods=['GET'])
def get_categories():
    try:
        conn = odbc.connect(connection_string)
        query = "SELECT CategoryName FROM Categories;"
        cursor = conn.cursor()
        cursor.execute(query)
        categories = [row[0] for row in cursor.fetchall()]  # Retrieve category names
        cursor.close()
        conn.close()
        
        return jsonify({"success": True, "categories": categories})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})
'''
@app.route('/get_categories', methods=['GET'])
def get_categories():
    # Check if the request contains the correct custom header
    if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return jsonify({"error": "Unauthorized access"}), 403

    try:
        conn = odbc.connect(connection_string)
        query = "SELECT CategoryName FROM Categories;"
        cursor = conn.cursor()
        cursor.execute(query)
        categories = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()

        return jsonify(categories)
    except Exception as e:
        return jsonify({"error": str(e)})
    

@app.route('/get_laptops', methods=['GET'])
def get_laptops():
    try:
        conn = odbc.connect(connection_string)
        query = "SELECT ModelName, Price FROM Laptops;"
        cursor = conn.cursor()
        cursor.execute(query)
        laptops = [{"model_name": row[0], "price": row[1]} for row in cursor.fetchall()]
        cursor.close()
        conn.close()

        return jsonify(laptops)
    except Exception as e:
        return jsonify({"error": str(e)})


if __name__ == '__main__':
    app.run(debug=True)
