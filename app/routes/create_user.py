from flask import Blueprint, render_template, jsonify, request
from app.services import get_db_connection
import pypyodbc as odbc

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

    if not first_name:
        return jsonify({"success": False, "message": "First name not completed."})
    if not last_name:
        return jsonify({"success": False, "message": "Last name not completed."})
    if not email:
        return jsonify({"success": False, "message": "Email not completed."})
    if not password:
        return jsonify({"success": False, "message": "Password not completed."})

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT 1 FROM Users WHERE Email = ?;", (email,))
        if cursor.fetchone():
            return jsonify({"success": False, "message": "Email already exists."})

        cursor.execute("""
            INSERT INTO Users (FirstName, LastName, Email, Password, PhoneNumber)
            VALUES (?, ?, ?, ?, ?);
        """, (first_name, last_name, email, password, phone_number))
        conn.commit()

        cursor.execute("SELECT UserID FROM Users WHERE Email = ?;", (email,))
        user_id = cursor.fetchone()[0]

        cursor.execute("""
            INSERT INTO ShoppingCart (UserID, CreationDate)
            VALUES (?, GETDATE());
        """, (user_id,))
        conn.commit()

        cursor.close()
        conn.close()
        return jsonify({"success": True})

    except Exception as e:
        return jsonify({"success": False, "message": str(e)})
