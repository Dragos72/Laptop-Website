from flask import Blueprint, render_template, redirect, jsonify, request, session
import pypyodbc as odbc
from app.services import get_db_connection  # Example helper function
from datetime import datetime

cart_blueprint = Blueprint('cart', __name__)

@cart_blueprint.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    try:
        data = request.json
        laptop_id = data.get('laptop_id')
        cart_id = session.get('CartID')

        if not cart_id:
            return jsonify({"success": False, "message": "No cart associated with the user."}), 403

        conn = get_db_connection()
        cursor = conn.cursor()

        check_query = "SELECT Quantity FROM CartLaptops WHERE CartID = ? AND LaptopID = ?"
        cursor.execute(check_query, (cart_id, laptop_id))
        result = cursor.fetchone()

        if result:
            update_query = "UPDATE CartLaptops SET Quantity = Quantity + 1 WHERE CartID = ? AND LaptopID = ?"
            cursor.execute(update_query, (cart_id, laptop_id))
        else:
            insert_query = "INSERT INTO CartLaptops (CartID, LaptopID, Quantity) VALUES (?, ?, ?)"
            cursor.execute(insert_query, (cart_id, laptop_id, 1))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"success": True, "message": "Laptop added to cart successfully!"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@cart_blueprint.route('/get_cart_items', methods=['GET'])
def get_cart_items():
    try:
        cart_id = session.get('CartID')
        if not cart_id:
            return jsonify({"success": False, "message": "No cart associated with the user."}), 403

        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
            SELECT 
                L.LaptopID,
                L.ModelName,
                L.Price,
                CL.Quantity,
                L.StockQuantity
            FROM CartLaptops CL
            JOIN Laptops L ON CL.LaptopID = L.LaptopID
            WHERE CL.CartID = ?;
        """
        cursor.execute(query, [cart_id])

        cart_items = [
            {
                "laptop_id": row[0],
                "model_name": row[1],
                "price": row[2],
                "quantity": row[3],
                "stock_quantity": row[4]
            }
            for row in cursor.fetchall()
        ]

        cursor.close()
        conn.close()

        return jsonify({"success": True, "items": cart_items})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@cart_blueprint.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    try:
        data = request.json
        laptop_id = data.get('laptop_id')
        cart_id = session.get('CartID')

        if not cart_id:
            return jsonify({"success": False, "message": "No cart session found."}), 403

        conn = get_db_connection()
        cursor = conn.cursor()

        delete_query = "DELETE FROM CartLaptops WHERE CartID = ? AND LaptopID = ?"
        cursor.execute(delete_query, (cart_id, laptop_id))
        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@cart_blueprint.route('/update_cart_quantities', methods=['POST'])
def update_cart_quantities():
    try:
        cart_id = session.get('CartID')
        if not cart_id:
            return jsonify({"success": False, "message": "No cart session found."}), 403

        data = request.get_json()
        items = data.get('items', [])

        conn = get_db_connection()
        cursor = conn.cursor()

        for item in items:
            laptop_id = item.get('laptop_id')
            quantity = item.get('quantity', 1)

            update_query = """
            UPDATE CartLaptops 
            SET Quantity = ? 
            WHERE CartID = ? AND LaptopID = ?
            """
            cursor.execute(update_query, (quantity, cart_id, laptop_id))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@cart_blueprint.route('/cart', methods=['GET'])
def cart_page():
    return render_template('cart.html')
