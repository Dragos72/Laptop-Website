from flask import Blueprint, render_template, session, redirect, jsonify, request
from app.services import get_db_connection


adminRoutes_blueprint = Blueprint('admin', __name__)

@adminRoutes_blueprint.route('/admin')
def admin_page():
    # Ensure only admins can access
    if session.get('UserType') != "A":
        return redirect('/')

    return render_template('admin.html')

@adminRoutes_blueprint.route('/admin/add_user', methods=['POST'])
def add_user():
    data = request.json
    try:
        conn = get_db_connection()
        query = """
        INSERT INTO Users (FirstName, LastName, Email, Password, PhoneNumber, UserType)
        VALUES (?, ?, ?, ?, ?, ?);
        """
        cursor = conn.cursor()
        cursor.execute(query, (data['firstName'], data['lastName'], data['email'], data['password'], data['phoneNumber'], data['userType']))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"success": True, "message": "User added successfully"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@adminRoutes_blueprint.route('/admin/remove_user', methods=['POST'])
def remove_user():
    data = request.json
    try:
        conn = get_db_connection()
        query = "DELETE FROM Users WHERE Email = ?;"
        cursor = conn.cursor()
        cursor.execute(query, (data['email'],))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"success": True, "message": "User removed successfully"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@adminRoutes_blueprint.route('/admin/modify_user', methods=['POST'])
def modify_user():
    data = request.json
    try:
        conn = get_db_connection()
        query = """
        UPDATE Users
        SET FirstName = ?, LastName = ?, Password = ?, PhoneNumber = ?, UserType = ?
        WHERE Email = ?;
        """
        cursor = conn.cursor()
        cursor.execute(query, (data['firstName'], data['lastName'], data['password'], data['phoneNumber'], data['userType'], data['email']))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"success": True, "message": "User modified successfully"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@adminRoutes_blueprint.route('/admin/add_category', methods=['POST'])
def add_category():
    data = request.json
    try:
        conn = get_db_connection()
        query = "INSERT INTO Categories (CategoryName, Description) VALUES (?, ?);"
        cursor = conn.cursor()
        cursor.execute(query, (data['categoryName'], data['description']))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"success": True, "message": "Category added successfully"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@adminRoutes_blueprint.route('/admin/add_laptop', methods=['POST'])
def add_laptop():
    data = request.json
    try:
        conn = get_db_connection()
        query = """
        INSERT INTO Laptops (ModelName, Price, StockQuantity, Processor, RAM, Storage, GraphicsCard, ScreenSize, Description)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
        """
        cursor = conn.cursor()
        cursor.execute(query, (data['modelName'], data['price'], data['stockQuantity'], data['processor'], data['ram'], data['storage'], data['graphicsCard'], data['screenSize'], data['description']))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"success": True, "message": "Laptop added successfully"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@adminRoutes_blueprint.route('/admin/execute_query/<query_name>', methods=['GET'])
def execute_query(query_name):
    queries = {
        "laptops_with_categories": """
            SELECT L.ModelName, C.CategoryName
            FROM Laptops L
            JOIN Categories C ON L.CategoryID = C.CategoryID;
        """,
        "users_with_cart": """
            SELECT U.FirstName, U.LastName, SC.CartID
            FROM Users U
            JOIN ShoppingCart SC ON U.UserID = SC.UserID;
        """,
        "laptops_in_cart": """
            SELECT SC.CartID, L.ModelName, CL.Quantity
            FROM CartLaptops CL
            JOIN Laptops L ON CL.LaptopID = L.LaptopID
            JOIN ShoppingCart SC ON CL.CartID = SC.CartID;
        """,
        "orders_with_users": """
            SELECT O.OrderID, U.FirstName, U.LastName, O.TotalAmount
            FROM Orders O
            JOIN Users U ON O.UserID = U.UserID;
        """,
        "laptops_with_brands": """
            SELECT L.ModelName, B.BrandName
            FROM Laptops L
            JOIN Brands B ON L.BrandID = B.BrandID;
        """,
        "user_addresses": """
            SELECT U.FirstName, U.LastName, A.Street, A.City, A.Country
            FROM Addresses A
            JOIN Users U ON A.UserID = U.UserID;
        """,
        "most_expensive_laptop": """
            SELECT ModelName, Price
            FROM Laptops
            WHERE Price = (SELECT MAX(Price) FROM Laptops);
        """,
        "top_customers": """
            SELECT U.FirstName, U.LastName, O.TotalAmount
            FROM Orders O
            JOIN Users U ON O.UserID = U.UserID
            WHERE O.TotalAmount > (SELECT AVG(TotalAmount) FROM Orders);
        """,
        "unused_laptops": """
            SELECT ModelName
            FROM Laptops
            WHERE LaptopID NOT IN (SELECT LaptopID FROM CartLaptops);
        """,
        "popular_categories": """
            SELECT C.CategoryName, COUNT(L.LaptopID) AS LaptopCount
            FROM Categories C
            JOIN Laptops L ON C.CategoryID = L.CategoryID
            GROUP BY C.CategoryName
            HAVING COUNT(L.LaptopID) > 5;
        """
    }

    query = queries.get(query_name)
    if not query:
        return jsonify({"success": False, "message": "Invalid query name."})

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        columns = [column[0] for column in cursor.description]

        results = [dict(zip(columns, row)) for row in rows]
        cursor.close()
        conn.close()

        return jsonify({"success": True, "results": results})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})
