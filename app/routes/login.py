from flask import Blueprint, render_template, jsonify, request
import pypyodbc as odbc
from app.services import get_db_connection  # Example helper function

login_blueprint = Blueprint('login', __name__)

@login_blueprint.route('/')
def login_page():
    return render_template('index.html')

@login_blueprint.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    try:
        conn = get_db_connection()
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