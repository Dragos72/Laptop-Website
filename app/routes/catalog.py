from flask import Blueprint, render_template, redirect, jsonify, request, session
import pypyodbc as odbc
from app.services import get_db_connection  # Example helper function
from datetime import datetime


catalog_blueprint = Blueprint('catalog', __name__)


@catalog_blueprint.route('/catalog')
def catalog():
    search_term = request.args.get('search', '').strip()
    category = request.args.get('category', '').strip()

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        if search_term:
            query = """
            SELECT LaptopID, ModelName, Price 
            FROM Laptops 
            WHERE ModelName LIKE ? AND StockQuantity > 0
            """
            cursor.execute(query, [f"%{search_term}%"])
        elif category:
            query = """
            SELECT L.LaptopID, L.ModelName, L.Price
            FROM Laptops L
            JOIN Categories C ON L.CategoryID = C.CategoryID
            WHERE C.CategoryName = ? AND L.StockQuantity > 0
            """
            cursor.execute(query, [category])
        else:
            query = "SELECT LaptopID, ModelName, Price FROM Laptops WHERE StockQuantity > 0"
            cursor.execute(query)

        laptops = [
            {"LaptopID": row[0], "ModelName": row[1], "Price": row[2]}
            for row in cursor.fetchall()
        ]

        return render_template('catalog.html', laptops=laptops)

    except Exception as e:
        return f"Error: {e}", 500
    finally:
        cursor.close()
        conn.close()


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
        query = "SELECT LaptopID, ModelName, Price FROM Laptops WHERE StockQuantity > 0;"
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
            SELECT LaptopID, ModelName, Price 
            FROM Laptops
            WHERE ModelName LIKE ?;
            """

            cursor.execute(query, [f"%{search_term}%"])
        else:
            # Query to fetch all laptops if no search term is provided
            query = "SELECT ModelName, Price FROM Laptops;"
            cursor.execute(query)

        laptops = [{"LaptopID": row[0], "ModelName": row[1], "Price": row[2]} for row in cursor.fetchall()]
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
        SELECT L.LaptopID, L.ModelName, L.Price 
        FROM Laptops L
        JOIN Categories C ON L.CategoryID = C.CategoryID
        WHERE C.CategoryName = ?;
        """

        cursor.execute(query, [category_name])

        # Fetch and format results
        laptops = [{"LaptopID": row[0], "ModelName": row[1], "Price": row[2]} for row in cursor.fetchall()]
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
    try:
        # Verifică dacă utilizatorul are un coș salvat în sesiune
        cart_id = session.get('CartID')
        if not cart_id:
            return jsonify({
                "success": False,
                "message": "No cart associated with the user."
            }), 403

        # Conectare la baza de date
        conn = get_db_connection()
        cursor = conn.cursor()

        # Interogare pentru a obține laptopurile din coș
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

        # Formatare rezultate într-o listă de dicționare
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

        # Închide cursorul și conexiunea
        cursor.close()
        conn.close()

        return jsonify({
            "success": True,
            "items": cart_items
        })

    except Exception as e:
        # Returnează o eroare dacă apare vreo excepție
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500



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

        
        conn = get_db_connection()
        cursor = conn.cursor()

        
        query_user = """
        SELECT FirstName, LastName, Email
        FROM Users
        WHERE UserID = ?;
        """
        cursor.execute(query_user, [user_id])
        user = cursor.fetchone()

        
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

       
        query = """
        INSERT INTO Addresses (UserID, Street, Number, City, PostalCode, Country, AddressType)
        VALUES (?, ?, ?, ?, ?, ?, ?);
        """
        cursor.execute(query, (user_id, street, number, city, postal_code, country, address_type))
        conn.commit()

        cursor.close()
        conn.close()

        
        return redirect('/myaccount')
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    
@catalog_blueprint.route('/get_address_details_by_street/<street>', methods=['GET'])
def get_address_details_by_street(street):
    """
    Fetch details for a specific address by Street name.
    """
    try:
        
        conn = get_db_connection()
        cursor = conn.cursor()

        
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

@catalog_blueprint.route('/submit_order', methods=['POST'])
def submit_order():
    try:
        user_id = session.get('UserID')
        cart_id = session.get('CartID')

        if not user_id or not cart_id:
            return jsonify({"success": False, "message": "User not logged in or no cart found"}), 403

        # We'll use a dummy total from JS (you still send it)
        data = request.get_json()
        total_amount = data.get('total_amount')
        if total_amount is None or total_amount <= 0:
            return jsonify({"success": False, "message": "Invalid total amount"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch cart items and their quantities
        cursor.execute("""
            SELECT CL.LaptopID, CL.Quantity, L.Price, L.StockQuantity
            FROM CartLaptops CL
            JOIN Laptops L ON CL.LaptopID = L.LaptopID
            WHERE CL.CartID = ?;
        """, (cart_id,))
        cart_items = cursor.fetchall()

        if not cart_items:
            return jsonify({"success": False, "message": "Cart is empty"}), 400

        # Check stock
        for laptop_id, quantity, price, stock_quantity in cart_items:
            if quantity > stock_quantity:
                return jsonify({"success": False, "message": f"Not enough stock for laptop ID {laptop_id}."}), 400

        # Insert order
        order_date = datetime.now().strftime('%Y-%m-%d')
        order_status = 'P'
        shipping_address_id = 2  # default
        billing_address_id = 2   # default
        cursor.execute("""
            INSERT INTO Orders (UserID, OrderDate, TotalAmount, ShippingAddressID, BillingAddressID, OrderStatus)
            VALUES (?, ?, ?, ?, ?, ?);
        """, (user_id, order_date, total_amount, shipping_address_id, billing_address_id, order_status))
        conn.commit()

        # Fetch new OrderID
        cursor.execute("""
            SELECT TOP 1 OrderID FROM Orders
            WHERE UserID = ? AND TotalAmount = ? AND OrderDate = ?
            ORDER BY OrderID DESC;
        """, (user_id, total_amount, order_date))
        order_id = cursor.fetchone()[0]

        # Insert into OrderLaptops + Subtract from stock
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

        # Insert dummy payment
        payment_date = datetime.now().strftime('%Y-%m-%d')
        payment_amount = total_amount
        payment_method = 'C'  # e.g., Card
        cursor.execute("""
            INSERT INTO Payments (OrderID, PaymentDate, PaymentAmount, PaymentMethod)
            VALUES (?, ?, ?, ?);
        """, (order_id, payment_date, payment_amount, payment_method))

        # Clear cart
        cursor.execute("DELETE FROM CartLaptops WHERE CartID = ?;", (cart_id,))
        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@catalog_blueprint.route('/signout')
def signout():
    session.clear() 
    return redirect('/')  


@catalog_blueprint.route('/autocomplete_laptops', methods=['GET'])
def autocomplete_laptops():
    try:
        query_term = request.args.get('term', '').strip()
        if not query_term:
            return jsonify([])

        conn = get_db_connection()
        cursor = conn.cursor()

        # Prioritize starts-with matches, then contains matches (excluding duplicates)
        cursor.execute("""
            SELECT TOP 3 ModelName
            FROM Laptops
            WHERE ModelName LIKE ? 
               OR (ModelName LIKE ? AND ModelName NOT LIKE ?)
            ORDER BY 
                CASE 
                    WHEN ModelName LIKE ? THEN 0 
                    ELSE 1 
                END,
                ModelName
        """, [f"{query_term}%", f"%{query_term}%", f"{query_term}%", f"{query_term}%"])

        suggestions = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()

        return jsonify(suggestions)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@catalog_blueprint.route('/remove_from_cart', methods=['POST'])
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



@catalog_blueprint.route('/update_cart_quantities', methods=['POST'])
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


@catalog_blueprint.route('/laptop/<int:laptop_id>', methods=['GET'])
def laptop_details(laptop_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Query all necessary info, including joins to Brand and Category
        query = """
        SELECT 
            L.LaptopID, L.ModelName, L.Description, L.Price, L.StockQuantity,
            L.Processor, L.RAM, L.Storage, L.GraphicsCard, L.ScreenSize,
            B.BrandName, C.CategoryName
        FROM Laptops L
        JOIN Brands B ON L.BrandID = B.BrandID
        JOIN Categories C ON L.CategoryID = C.CategoryID
        WHERE L.LaptopID = ?;
        """
        cursor.execute(query, (laptop_id,))
        row = cursor.fetchone()

        laptop = {
            "LaptopID": row[0],
            "ModelName": row[1],
            "Description": row[2],
            "Price": row[3],
            "StockQuantity": row[4],
            "Processor": row[5],
            "RAM": row[6],
            "Storage": row[7],
            "GraphicsCard": row[8],
            "ScreenSize": row[9],
            "BrandName": row[10],
            "CategoryName": row[11]
        }

        # After fetching main laptop data
        first_letter = laptop["ModelName"][0].upper()

        cursor.execute("""
            SELECT TOP 4 LaptopID, ModelName, Price
            FROM Laptops
            WHERE (
                UPPER(ModelName) LIKE ? 
                OR UPPER(ModelName) LIKE ?
            ) AND LaptopID != ? AND StockQuantity > 0
            ORDER BY 
                CASE 
                    WHEN UPPER(ModelName) LIKE ? THEN 0
                    ELSE 1
                END,
                ModelName
        """, [f"{first_letter}%", f"%{first_letter}%", laptop_id, f"{first_letter}%"])


        suggestions = [
            {"LaptopID": row[0], "ModelName": row[1], "Price": row[2]}
            for row in cursor.fetchall()
        ]

        cursor.close()
        conn.close()

        if not row:
            return render_template('404.html'), 404

        

        

        return render_template("laptop_details.html", laptop=laptop, suggestions=suggestions)


    except Exception as e:
        return jsonify({"error": str(e)}), 500
