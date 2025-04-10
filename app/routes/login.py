from flask import Blueprint, render_template, jsonify, request, session
from app.services import get_db_connection
import pypyodbc as odbc

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
        cursor = conn.cursor()

        cursor.execute("""
            SELECT UserID, FirstName, LastName, UserType
            FROM Users
            WHERE Email = ? AND Password = ?;
        """, (email, password))
        user = cursor.fetchone()

        if not user:
            cursor.close()
            conn.close()
            return jsonify({"success": False, "message": "Invalid email or password."})

        user_id, _, _, user_type = user

        cursor.execute("""
            SELECT CartID
            FROM ShoppingCart
            WHERE UserID = ?;
        """, (user_id,))
        cart = cursor.fetchone()

        if not cart:
            cursor.execute("""
                INSERT INTO ShoppingCart (UserID, CreationDate)
                OUTPUT INSERTED.CartID
                VALUES (?, GETDATE());
            """, (user_id,))
            cart_id = cursor.fetchone()[0]
            conn.commit()
        else:
            cart_id = cart[0]

        session['UserID'] = user_id
        session['CartID'] = cart_id
        session['UserType'] = user_type

        cursor.close()
        conn.close()

        redirect_url = "/admin" if user_type == "A" else "/catalog"
        return jsonify({"success": True, "redirect": redirect_url})

    except Exception as e:
        return jsonify({"success": False, "message": str(e)})
