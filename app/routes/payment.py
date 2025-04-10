from flask import Blueprint, render_template, jsonify, session
from app.services import get_db_connection

payment_blueprint = Blueprint('payment', __name__)


@payment_blueprint.route('/payment', methods=['GET'])
def payment_page():
    """
    Render the payment page with addresses for shipping and billing.
    """
    try:
        user_id = session.get('UserID')
        if not user_id:
            return jsonify({"success": False, "message": "User is not logged in"}), 403

        conn = get_db_connection()
        cursor = conn.cursor()

        query_addresses = """
        SELECT AddressID, Street, Number, City, PostalCode, Country, AddressType
        FROM Addresses
        WHERE UserID = ?;
        """
        cursor.execute(query_addresses, [user_id])
        addresses = [
            {
                "AddressID": row[0],
                "Street": row[1],
                "Number": row[2],
                "City": row[3],
                "PostalCode": row[4],
                "Country": row[5],
                "AddressType": row[6],
            }
            for row in cursor.fetchall()
        ]

        cursor.close()
        conn.close()

        shipping_addresses = [addr for addr in addresses if addr["AddressType"] == "S"]
        billing_addresses = [addr for addr in addresses if addr["AddressType"] == "B"]

        return render_template(
            'payment.html',
            shipping_addresses=shipping_addresses,
            billing_addresses=billing_addresses
        )
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
