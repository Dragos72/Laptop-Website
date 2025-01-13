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
    

@adminRoutes_blueprint.route('/admin/remove_category', methods=['POST'])
def remove_category():
    data = request.json
    try:
        conn = get_db_connection()
        query = "DELETE FROM Categories WHERE CategoryName = ?;"
        cursor = conn.cursor()
        cursor.execute(query, (data['categoryName'],))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"success": True, "message": "Category removed successfully"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@adminRoutes_blueprint.route('/admin/update_category', methods=['POST'])
def update_category():
    data = request.json
    try:
        conn = get_db_connection()
        query = """
        UPDATE Categories
        SET Description = ?
        WHERE CategoryName = ?;
        """
        cursor = conn.cursor()
        cursor.execute(query, (data['newDescription'], data['categoryName']))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"success": True, "message": "Category updated successfully"})
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
    param = request.args.get('param', None)

    queries = {

        #Simple

        "laptops_by_brand": """
            SELECT L.ModelName, B.BrandName
            FROM Laptops L
            JOIN Brands B ON L.BrandID = B.BrandID
            WHERE B.BrandName = ?;
        """,
        "popular_brands":"""
        SELECT B.BrandName, COUNT(L.LaptopID) AS LaptopCount
        FROM Brands B
        JOIN Laptops L ON B.BrandID = L.CategoryID
        GROUP BY B.BrandName
        HAVING COUNT(L.LaptopID) >= ?;
        """,
        "total_orders_by_user":"""
        SELECT U.FirstName, U.LastName, COUNT(O.OrderID) AS OrderCount, SUM(O.TotalAmount) AS TotalAmount
        FROM Users U
        JOIN Orders O ON U.UserID = O.UserID
        GROUP BY U.FirstName, U.LastName
        HAVING SUM(O.TotalAmount) >= ?;
        """,

        "total_stock_by_brand":"""
        SELECT B.BrandName, SUM(L.Price * L.StockQuantity) AS TotalStockValue
        FROM Laptops L
        JOIN Brands B ON L.BrandID = B.BrandID
        WHERE B.BrandName = ? -- Replace ? with the brand name (parameter)
        GROUP BY B.BrandName;
        """,

        "average_price_by_category":"""
        SELECT C.CategoryName, AVG(L.Price) AS AverageLaptopPrice
        FROM Laptops L
        JOIN Categories C ON L.CategoryID = C.CategoryID
        WHERE C.CategoryName = ? -- Replace ? with the category name (parameter)
        GROUP BY C.CategoryName;
        """,

        "popular_categories":"""
        SELECT C.CategoryName, COUNT(L.LaptopID) AS LaptopCount
        FROM Categories C
        JOIN Laptops L ON C.CategoryID = L.CategoryID
        GROUP BY C.CategoryName
        HAVING COUNT(L.LaptopID) >= ?;
        """,


        #Complex

        "most_expensive_laptop_by_brand":"""
        SELECT L.ModelName, L.Price
        FROM Laptops L
        WHERE L.Price = (
            SELECT MAX(L2.Price)
            FROM Laptops L2
            JOIN Brands B ON L2.BrandID = B.BrandID
            WHERE B.BrandName = ?
        );
        """,

        "users_with_high_spending": """
        SELECT U.FirstName, U.LastName, SUM(O.TotalAmount) AS TotalSpent
        FROM Users U
        JOIN Orders O ON U.UserID = O.UserID
        GROUP BY U.FirstName, U.LastName
        HAVING SUM(O.TotalAmount) >= ?
        AND SUM(O.TotalAmount) >= (
            SELECT AVG(TotalAmount) FROM Orders
        );
        """,

        "laptops_not_in_cart":"""
        SELECT L.ModelName
        FROM Laptops L
        WHERE L.Price > ?
        AND L.LaptopID NOT IN (
            SELECT DISTINCT CL.LaptopID FROM CartLaptops CL
        );
        """,

        "categories_with_high_stock":"""
        SELECT 
        C.CategoryName,
        COUNT(L.LaptopID) AS LaptopCount
        FROM 
            Categories C
        JOIN 
            Laptops L ON C.CategoryID = L.CategoryID
        WHERE 
            L.Price >= ?
            AND L.LaptopID NOT IN (
                SELECT DISTINCT OL.LaptopID
                FROM OrderLaptops OL
            )
        GROUP BY 
            C.CategoryName
        ORDER BY 
        LaptopCount DESC;
        """,

        "no_payment_users":"""
        SELECT 
        U.FirstName, 
        U.LastName, 
        U.Email
        FROM 
            Users U
        WHERE 
        U.UserID NOT IN (
            SELECT DISTINCT O.UserID
            FROM Orders O
            JOIN Payments P ON O.OrderID = P.OrderID
            WHERE YEAR(P.PaymentDate) >= ?
        );
        """,

    }

    query = queries.get(query_name)
    if not query:
        return jsonify({"success": False, "message": "Invalid query name."})

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, (param,))
        rows = cursor.fetchall()
        columns = [column[0] for column in cursor.description]

        results = [dict(zip(columns, row)) for row in rows]
        cursor.close()
        conn.close()

        return jsonify({"success": True, "results": results})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


