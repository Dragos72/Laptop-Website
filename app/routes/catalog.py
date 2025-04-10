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
