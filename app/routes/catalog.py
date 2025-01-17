from flask import Blueprint, render_template, redirect, jsonify, request, session
import pypyodbc as odbc
from app.services import get_db_connection  # Example helper function
from datetime import datetime


catalog_blueprint = Blueprint('catalog', __name__)


@catalog_blueprint.route('/catalog')
def catalog():
    # You may fetch categories and laptop data from your database here
    return render_template('catalog.html')

@catalog_blueprint.route('/get_categories', methods=['GET'])
def get_categories():
    # Check if the request contains the correct custom header
    if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return jsonify({"error": "Unauthorized access"}), 403

    try:
        conn = get_db_connection()
        query = "SELECT CategoryName FROM Categories;"
        cursor = conn.cursor()
        cursor.execute(query)
        categories = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()

        return jsonify(categories)
    except Exception as e:
        return jsonify({"error": str(e)})
    

@catalog_blueprint.route('/get_laptops', methods=['GET'])
def get_laptops():
    try:
        conn = get_db_connection()
        query = "SELECT LaptopID, ModelName, Price FROM Laptops;"
        cursor = conn.cursor()
        cursor.execute(query)
        laptops = [{"LaptopID": row[0], "ModelName": row[1], "Price": row[2]} for row in cursor.fetchall()]
        cursor.close()
        conn.close()

        return jsonify(laptops)
    except Exception as e:
        return jsonify({"error": str(e)})
    
@catalog_blueprint.route('/search_laptops', methods=['POST'])
def search_laptops():
    try:
        data = request.json  # Get the JSON payload from the frontend
        search_term = data.get('search_term', '').strip()

        conn = get_db_connection()
        cursor = conn.cursor()

        # Query to fetch laptops based on the search term
        if search_term:
            query = """
            SELECT ModelName, Price 
            FROM Laptops
            WHERE ModelName LIKE ?;
            """
            cursor.execute(query, [f"%{search_term}%"])
        else:
            # Query to fetch all laptops if no search term is provided
            query = "SELECT ModelName, Price FROM Laptops;"
            cursor.execute(query)

        laptops = [{"model_name": row[0], "price": row[1]} for row in cursor.fetchall()]
        cursor.close()
        conn.close()

        return jsonify({"success": True, "laptops": laptops})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})
    

@catalog_blueprint.route('/filter_laptops', methods=['POST'])
def filter_laptops():
    """
    This route fetches laptops filtered by category.
    """
    try:
        # Get the category name from the JSON payload
        data = request.json
        category_name = data.get('category_name')

        if not category_name:
            return jsonify({"success": False, "message": "Category name is required"}), 400

        # Connect to the database
        conn = get_db_connection()
        cursor = conn.cursor()

        # Query to fetch laptops based on the category
        query = """
        SELECT L.ModelName, L.Price 
        FROM Laptops L
        JOIN Categories C ON L.CategoryID = C.CategoryID
        WHERE C.CategoryName = ?;
        """
        cursor.execute(query, [category_name])

        # Fetch and format results
        laptops = [{"model_name": row[0], "price": row[1]} for row in cursor.fetchall()]
        cursor.close()
        conn.close()

        # Return the filtered laptops
        return jsonify({"success": True, "laptops": laptops})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    
@catalog_blueprint.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    """
    Add a laptop to the cart. If the laptop already exists in the cart, increment the quantity.
    """
    try:
        data = request.json
        laptop_id = data.get('laptop_id')

        # Ensure the user is logged in and has a CartID
        cart_id = session.get('CartID')
        if not cart_id:
            return jsonify({"success": False, "message": "No cart associated with the user."}), 403

        # Connect to the database
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if the laptop is already in the cart
        check_query = "SELECT Quantity FROM CartLaptops WHERE CartID = ? AND LaptopID = ?"
        cursor.execute(check_query, (cart_id, laptop_id))
        result = cursor.fetchone()

        if result:
            # If the laptop exists in the cart, increment the quantity
            update_query = "UPDATE CartLaptops SET Quantity = Quantity + 1 WHERE CartID = ? AND LaptopID = ?"
            cursor.execute(update_query, (cart_id, laptop_id))
        else:
            # If the laptop is not in the cart, insert a new record
            insert_query = "INSERT INTO CartLaptops (CartID, LaptopID, Quantity) VALUES (?, ?, ?)"
            cursor.execute(insert_query, (cart_id, laptop_id, 1))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"success": True, "message": "Laptop added to cart successfully!"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

    


@catalog_blueprint.route('/get_cart_items', methods=['GET'])
def get_cart_items():
    """
    Fetch all items in the user's cart and return their details.
    """
    try:
        # Ensure the user is logged in and has a CartID
        cart_id = session.get('CartID')
        if not cart_id:
            return jsonify({"success": False, "message": "No cart associated with the user."}), 403

        # Connect to the database
        conn = get_db_connection()
        cursor = conn.cursor()

        # Query to get cart items
        query = """
        SELECT L.ModelName, L.Price, CL.Quantity
        FROM CartLaptops CL
        JOIN Laptops L ON CL.LaptopID = L.LaptopID
        WHERE CL.CartID = ?;
        """
        cursor.execute(query, [cart_id])

        # Fetch and format the results
        cart_items = [
            {"model_name": row[0], "price": row[1], "quantity": row[2]}
            for row in cursor.fetchall()
        ]

        cursor.close()
        conn.close()

        # Return the cart items as JSON
        return jsonify({"success": True, "items": cart_items})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500



@catalog_blueprint.route('/cart', methods=['GET'])
def cart_page():
    """
    Render the cart page.
    """
    return render_template('cart.html')

@catalog_blueprint.route('/payment', methods=['GET'])
def payment_page():
    """
    Render the payment page with addresses for shipping and billing.
    """
    try:
        # Get UserID from session
        user_id = session.get('UserID')
        if not user_id:
            return jsonify({"success": False, "message": "User is not logged in"}), 403

        # Connect to the database
        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch Shipping and Billing addresses
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

        # Separate Shipping and Billing addresses
        shipping_addresses = [addr for addr in addresses if addr["AddressType"] == "S"]
        billing_addresses = [addr for addr in addresses if addr["AddressType"] == "B"]

        return render_template(
            'payment.html',
            shipping_addresses=shipping_addresses,
            billing_addresses=billing_addresses
        )
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@catalog_blueprint.route('/myaccount', methods=['GET'])
def myaccount():
    """
    Render the MyAccount page with user details and addresses.
    """
    try:
        # Get UserID from session
        user_id = session.get('UserID')
        if not user_id:
            return jsonify({"success": False, "message": "User is not logged in"}), 403

        # Connect to the database
        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch user details
        query_user = """
        SELECT FirstName, LastName, Email
        FROM Users
        WHERE UserID = ?;
        """
        cursor.execute(query_user, [user_id])
        user = cursor.fetchone()

        # Fetch addresses for the user
        query_addresses = """
        SELECT Street, Number, City, PostalCode, Country, AddressType
        FROM Addresses
        WHERE UserID = ?;
        """
        cursor.execute(query_addresses, [user_id])
        addresses = [
            {
                "Street": row[0],
                "Number": row[1],
                "City": row[2],
                "PostalCode": row[3],
                "Country": row[4],
                "AddressType": "Shipping" if row[5] == "S" else "Billing",
            }
            for row in cursor.fetchall()
        ]

        cursor.close()
        conn.close()

        # Render MyAccount page
        return render_template(
            'myaccount.html',
            user={"FirstName": user[0], "LastName": user[1], "Email": user[2]},
            addresses=addresses
        )
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@catalog_blueprint.route('/add_address', methods=['GET'])
def add_address():
    """
    Render the add address page.
    """
    return render_template('add_address.html')


@catalog_blueprint.route('/submit_address', methods=['POST'])
def submit_address():
    """
    Handles the submission of a new address and inserts it into the Addresses table.
    """
    try:
        # Get UserID from the session
        user_id = session.get('UserID')
        if not user_id:
            return jsonify({"success": False, "message": "User is not logged in"}), 403

        # Get the form data
        street = request.form.get('street')
        number = request.form.get('number')
        city = request.form.get('city')
        postal_code = request.form.get('postalcode')
        country = request.form.get('country')
        address_type = request.form.get('type')

        # Connect to the database
        conn = get_db_connection()
        cursor = conn.cursor()

        # Insert the new address
        query = """
        INSERT INTO Addresses (UserID, Street, Number, City, PostalCode, Country, AddressType)
        VALUES (?, ?, ?, ?, ?, ?, ?);
        """
        cursor.execute(query, (user_id, street, number, city, postal_code, country, address_type))
        conn.commit()

        cursor.close()
        conn.close()

        # Redirect back to the MyAccount page
        return redirect('/myaccount')
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    
@catalog_blueprint.route('/get_address_details_by_street/<street>', methods=['GET'])
def get_address_details_by_street(street):
    """
    Fetch details for a specific address by Street name.
    """
    try:
        # Connect to the database
        conn = get_db_connection()
        cursor = conn.cursor()

        # Query to fetch address details
        query = """
        SELECT Street, Number, City, PostalCode, Country
        FROM Addresses
        WHERE Street = ?;
        """
        cursor.execute(query, [street])
        row = cursor.fetchone()

        if row:
            address = {
                "Street": row[0],
                "Number": row[1],
                "City": row[2],
                "PostalCode": row[3],
                "Country": row[4],
            }
            return jsonify({"success": True, "address": address})
        else:
            return jsonify({"success": False, "message": "Address not found"}), 404
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@catalog_blueprint.route('/submit_payment', methods=['POST'])
def submit_payment():
    try:
        # Get UserID from session
        user_id = session.get('UserID')
        if not user_id:
            return jsonify({"success": False, "message": "User is not logged in"}), 403

        # Parse JSON data from the request
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "Invalid or missing JSON payload"}), 400

        total_amount = data.get('total_amount')
        if total_amount is None or total_amount <= 0:
            return jsonify({"success": False, "message": "Invalid total amount provided."}), 400

        payment_amount = total_amount
        payment_method = 'C'  # Default payment method

        # Ensure the user has a cart associated
        cart_id = session.get('CartID')
        if not cart_id:
            return jsonify({"success": False, "message": "No cart associated with the user."}), 403

        conn = get_db_connection()
        cursor = conn.cursor()

        # Insert the order into Orders table
        order_date = datetime.now().strftime('%Y-%m-%d')
        order_status = 'P'  # Pending
        shipping_address_id = 2  # Example value, replace with actual shipping address
        billing_address_id = 2  # Example value, replace with actual billing address
        insert_order_query = """
        INSERT INTO Orders (UserID, OrderDate, TotalAmount, ShippingAddressID, BillingAddressID, OrderStatus)
        VALUES (?, ?, ?, ?, ?, ?);
        """
        cursor.execute(insert_order_query, (user_id, order_date, total_amount, shipping_address_id, billing_address_id, order_status))
        conn.commit()

        # Retrieve the OrderID of the newly inserted order
        fetch_order_query = """
        SELECT TOP 1 OrderID FROM Orders
        WHERE UserID = ? AND TotalAmount = ? AND OrderStatus = ? AND OrderDate = ?
        ORDER BY OrderID DESC;
        """
        cursor.execute(fetch_order_query, (user_id, total_amount, order_status, order_date))
        order_row = cursor.fetchone()
        if not order_row:
            return jsonify({"success": False, "message": "Failed to fetch the OrderID."}), 500
        order_id = order_row[0]

        # Insert payment record into Payments table
        payment_date = datetime.now().strftime('%Y-%m-%d')
        insert_payment_query = """
        INSERT INTO Payments (OrderID, PaymentDate, PaymentAmount, PaymentMethod)
        VALUES (?, ?, ?, ?);
        """
        cursor.execute(insert_payment_query, (order_id, payment_date, payment_amount, payment_method))
        conn.commit()

        # Fetch cart items to insert into OrderLaptops
        fetch_cart_items_query = """
        SELECT CL.LaptopID, CL.Quantity, L.Price
        FROM CartLaptops CL
        JOIN Laptops L ON CL.LaptopID = L.LaptopID
        WHERE CL.CartID = ?;
        """
        cursor.execute(fetch_cart_items_query, (cart_id,))
        cart_items = cursor.fetchall()

        # Insert each cart item into OrderLaptops
        insert_order_laptops_query = """
        INSERT INTO OrderLaptops (OrderID, LaptopID, Quantity, Price)
        VALUES (?, ?, ?, ?);
        """
        for item in cart_items:
            laptop_id, quantity, price = item
            cursor.execute(insert_order_laptops_query, (order_id, laptop_id, quantity, price))
        conn.commit()

        # Clear the user's cart after the order is placed
        clear_cart_query = "DELETE FROM CartLaptops WHERE CartID = ?;"
        cursor.execute(clear_cart_query, (cart_id,))
        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({"success": True, "message": "Order submitted successfully!"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
