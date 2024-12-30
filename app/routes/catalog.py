from flask import Blueprint, render_template, jsonify, request, session
import pypyodbc as odbc
from app.services import get_db_connection  # Example helper function
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
    This route adds a laptop to the cart by inserting a record into the CartLaptops table.
    """
    try:
        data = request.json  # Get the JSON payload from the frontend
        laptop_id = data.get('laptop_id')  # Extract the laptop ID from the request

        # Ensure the user is logged in and has a CartID
        cart_id = session.get('CartID')
        if not cart_id:
            return jsonify({"success": False, "message": "No cart associated with the user."}), 403

        # Default quantity
        quantity = 1

        # Connect to the database
        conn = get_db_connection()
        cursor = conn.cursor()

        # Insert the new record into the CartLaptops table
        query = """
        INSERT INTO CartLaptops (CartID, LaptopID, Quantity)
        VALUES (?, ?, ?);
        """
        cursor.execute(query, (cart_id, laptop_id, quantity))
        conn.commit()  # Commit the transaction

        cursor.close()
        conn.close()

        return jsonify({"success": True, "message": "Laptop added to cart successfully!"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500