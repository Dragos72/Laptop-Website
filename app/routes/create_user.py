from flask import Blueprint, render_template, jsonify, request
import pypyodbc as odbc
from app.services import get_db_connection 

create_user_blueprint = Blueprint('create_user', __name__)

@create_user_blueprint.route('/create_account')
def create_account():
    return render_template('createUser.html')

@create_user_blueprint.route('/create_user', methods=['POST'])
def create_user():
    data = request.get_json()
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    email = data.get('email')
    password = data.get('password')
    phone_number = data.get('phone_number')

    # Verify that each element is not empty
    if not first_name:
        return jsonify({"success": False, "message": "First name not completed."})

    if not last_name:
        return jsonify({"success": False, "message": "Last name not completed."})

    if not email:
        return jsonify({"success": False, "message": "Email not completed."})

    if not password:
        return jsonify({"success": False, "message": "Password not completed."})

    # If all fields are completed, proceed with opening the connection to the database
    try:
        # Connect to the database
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if email already exists
        email_check_query = "SELECT 1 FROM Users WHERE Email = ?;"
        cursor.execute(email_check_query, (email,))
        if cursor.fetchone():
            return jsonify({"success": False, "message": "Email already exists."})

        # Insert the new user
        insert_user_query = """
        INSERT INTO Users (FirstName, LastName, Email, Password, PhoneNumber)
        VALUES (?, ?, ?, ?, ?);
        """
        cursor.execute(insert_user_query, (first_name, last_name, email, password, phone_number))
        conn.commit()

        # Retrieve the UserID of the newly inserted user
        user_id_query = "SELECT UserID FROM Users WHERE Email = ?;"
        cursor.execute(user_id_query, (email,))
        user_id = cursor.fetchone()[0]

        # Insert into ShoppingCart with the retrieved UserID
        insert_cart_query = """
        INSERT INTO ShoppingCart (UserID, CreationDate)
        VALUES (?, GETDATE());
        """
        cursor.execute(insert_cart_query, (user_id,))
        conn.commit()

        # Close the database connection
        cursor.close()
        conn.close()

        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})
    