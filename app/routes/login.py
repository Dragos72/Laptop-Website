from flask import Blueprint, render_template, jsonify, request, session
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

        # Query to check user credentials
        query_user = """
        SELECT UserID, FirstName, LastName
        FROM Users
        WHERE Email = ? AND Password = ?;
        """
        cursor = conn.cursor()
        cursor.execute(query_user, (email, password))
        user = cursor.fetchone()

        if user:
            # Retrieve or create CartID for the user
            user_id = user[0]
            query_cart = """
            SELECT CartID
            FROM ShoppingCart
            WHERE UserID = ?;
            """
            cursor.execute(query_cart, (user_id,))
            cart = cursor.fetchone()

            if not cart:
                # If no cart exists, create one
                query_create_cart = """
                INSERT INTO ShoppingCart (UserID, CreationDate)
                OUTPUT INSERTED.CartID
                VALUES (?, GETDATE());
                """
                cursor.execute(query_create_cart, (user_id,))
                cart_id = cursor.fetchone()[0]
                conn.commit()
            else:
                cart_id = cart[0]

            # Store UserID and CartID in session
            session['UserID'] = user_id
            session['CartID'] = cart_id

            cursor.close()
            conn.close()

            # Login successful, return success response
            return jsonify({"success": True, "first_name": user[1], "last_name": user[2]})
        else:
            # Login failed, send a failure message
            cursor.close()
            conn.close()
            return jsonify({"success": False, "message": "Invalid email or password."})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})