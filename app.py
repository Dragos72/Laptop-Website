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

@app.route('/mainPage')
def main_page():
    return render_template('main_page.html')

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

if __name__ == '__main__':
    app.run(debug=True)
