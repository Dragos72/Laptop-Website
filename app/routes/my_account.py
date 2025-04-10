from flask import Blueprint, render_template, request, redirect, session, jsonify
from app.services import get_db_connection

my_account_blueprint = Blueprint('myaccount', __name__)

@my_account_blueprint.route('/myaccount', methods=['GET'])
def myaccount():
    try:
        user_id = session.get('UserID')
        if not user_id:
            return jsonify({"success": False, "message": "User is not logged in"}), 403

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT FirstName, LastName, Email
            FROM Users
            WHERE UserID = ?;
        """, [user_id])
        user = cursor.fetchone()

        cursor.execute("""
            SELECT Street, Number, City, PostalCode, Country, AddressType
            FROM Addresses
            WHERE UserID = ?;
        """, [user_id])
        addresses = [
            {
                "Street": row[0],
                "Number": row[1],
                "City": row[2],
                "PostalCode": row[3],
                "Country": row[4],
                "AddressType": "Shipping" if row[5] == "S" else "Billing",
            } for row in cursor.fetchall()
        ]

        cursor.close()
        conn.close()

        return render_template('myaccount.html', user={
            "FirstName": user[0], "LastName": user[1], "Email": user[2]
        }, addresses=addresses)

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@my_account_blueprint.route('/add_address', methods=['GET'])
def add_address():
    return render_template('add_address.html')


@my_account_blueprint.route('/submit_address', methods=['POST'])
def submit_address():
    try:
        user_id = session.get('UserID')
        if not user_id:
            return jsonify({"success": False, "message": "User is not logged in"}), 403

        street = request.form.get('street')
        number = request.form.get('number')
        city = request.form.get('city')
        postal_code = request.form.get('postalcode')
        country = request.form.get('country')
        address_type = request.form.get('type')

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO Addresses (UserID, Street, Number, City, PostalCode, Country, AddressType)
            VALUES (?, ?, ?, ?, ?, ?, ?);
        """, (user_id, street, number, city, postal_code, country, address_type))
        conn.commit()

        cursor.close()
        conn.close()

        return redirect('/my_account')

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@my_account_blueprint.route('/get_address_details_by_street/<street>', methods=['GET'])
def get_address_details_by_street(street):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT Street, Number, City, PostalCode, Country
            FROM Addresses
            WHERE Street = ?;
        """, [street])
        row = cursor.fetchone()

        if row:
            address = {
                "Street": row[0],
                "Number": row[1],
                "City": row[2],
                "PostalCode": row[3],
                "Country": row[4]
            }
            return jsonify({"success": True, "address": address})
        else:
            return jsonify({"success": False, "message": "Address not found"}), 404

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
