import pypyodbc as odbc

def get_db_connection():
    DRIVER_NAME = 'SQL SERVER'
    #SERVER_NAME = 'DESKTOP-NEGON5B\SQLEXPRESS'
    SERVER_NAME = 'DRAGOS\SQLEXPRESS'
    DATABASE_NAME = 'Website_Database'

    connection_string = f"""
        DRIVER={{{DRIVER_NAME}}};
        SERVER={SERVER_NAME};
        DATABASE={DATABASE_NAME};
        Trust_Connection=yes;
    """
    return odbc.connect(connection_string)