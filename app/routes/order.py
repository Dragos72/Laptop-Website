from flask import Blueprint, jsonify, request, session, redirect
from app.services import get_db_connection
from datetime import datetime

order_blueprint = Blueprint('order', __name__)


@order_blueprint.route('/submit_order', methods=['POST'])
def submit_order():
    try:
        user_id = session.get('UserID')
        cart_id = session.get('CartID')

        if not user_id or not cart_id:
            return jsonify({"success": False, "message": "User not logged in or no cart found"}), 403

        data = request.get_json()
        total_amount = data.get('total_amount')
        if total_amount is None or total_amount <= 0:
            return jsonify({"success": False, "message": "Invalid total amount"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT CL.LaptopID, CL.Quantity, L.Price, L.StockQuantity
            FROM CartLaptops CL
            JOIN Laptops L ON CL.LaptopID = L.LaptopID
            WHERE CL.CartID = ?;
        """, (cart_id,))
        cart_items = cursor.fetchall()

        if not cart_items:
            return jsonify({"success": False, "message": "Cart is empty"}), 400

        for laptop_id, quantity, price, stock_quantity in cart_items:
            if quantity > stock_quantity:
                return jsonify({"success": False, "message": f"Not enough stock for laptop ID {laptop_id}."}), 400

        order_date = datetime.now().strftime('%Y-%m-%d')
        order_status = 'P'
        shipping_address_id = 2
        billing_address_id = 2

        cursor.execute("""
            INSERT INTO Orders (UserID, OrderDate, TotalAmount, ShippingAddressID, BillingAddressID, OrderStatus)
            VALUES (?, ?, ?, ?, ?, ?);
        """, (user_id, order_date, total_amount, shipping_address_id, billing_address_id, order_status))
        conn.commit()

        cursor.execute("""
            SELECT TOP 1 OrderID FROM Orders
            WHERE UserID = ? AND TotalAmount = ? AND OrderDate = ?
            ORDER BY OrderID DESC;
        """, (user_id, total_amount, order_date))
        order_id = cursor.fetchone()[0]

        for laptop_id, quantity, price, stock_quantity in cart_items:
            cursor.execute("""
                INSERT INTO OrderLaptops (OrderID, LaptopID, Quantity, Price)
                VALUES (?, ?, ?, ?);
            """, (order_id, laptop_id, quantity, price))

            cursor.execute("""
                UPDATE Laptops
                SET StockQuantity = StockQuantity - ?
                WHERE LaptopID = ?;
            """, (quantity, laptop_id))

        payment_date = datetime.now().strftime('%Y-%m-%d')
        payment_amount = total_amount
        payment_method = 'C'

        cursor.execute("""
            INSERT INTO Payments (OrderID, PaymentDate, PaymentAmount, PaymentMethod)
            VALUES (?, ?, ?, ?);
        """, (order_id, payment_date, payment_amount, payment_method))

        cursor.execute("DELETE FROM CartLaptops WHERE CartID = ?;", (cart_id,))
        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
