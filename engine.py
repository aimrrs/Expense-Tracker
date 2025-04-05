<<<<<<< HEAD
import config
import mysql.connector as mysql
from datetime import date
import pandas as pd
from random import randint

class Otp:
    pass

def writeErrLog(msg):
    with open("log/err.log", "a") as file_object:
        file_object.write(msg+"\n\n")

# Getting username and password.
USERNAME = config.DB_USERNAME
PASSWD = config.DB_PASSWORD

# Creating instance for connection.
myConn = mysql.connect(user=USERNAME, password=PASSWD, host="0.0.0.0")
cursor = myConn.cursor()

# Getting the 'D, M, Y' of current day.
td = date.today()
M, Y = td.month, td.year

if len(str(M)) == 1:
    TABLENAME = f"m0{M}_{Y}"
else:
    TABLENAME = f"m{M}_{Y}"

def otp_generate(email):
    otp = str(randint(100000, 999999))
    try:
        cursor.execute("USE userinformation")
        cursor.execute(f"SELECT * FROM otp WHERE email = '{email}'")
        result = cursor.fetchall()
        if not result:
            cursor.execute(f"INSERT INTO otp(email, otp_num) VALUES('{email}', {otp})")
            myConn.commit()
            return "OTP:NOT_EXISTS", otp
        else:
            return "OTP:EXISTS", otp
    except mysql.Error as err:
        writeErrLog(str(err))
        return {'success' : False, 'err' : str(err)}

def otp_verify(email, otp):
    try:
        cursor.execute("USE userinformation")
        cursor.execute(f"SELECT * FROM otp WHERE email = '{email}'")
        result = cursor.fetchall()
        if otp == result[0][1]:
            cursor.execute(f"DELETE FROM otp WHERE email = '{email}'")
            myConn.commit()
            return {'success' : True}, 1
        else:
            return {'success' : False}, 0
    except mysql.Error as err:
        writeErrLog(str(err))
        return {'success' : False, 'error' : str(err)}

class General:
    """
    General consists
        1. To check is user is registered       registered()
        2. To create new user profile           newUser(<name, institute, region>)
        3. To check if user db exists and use   useDB()
        4. To create db for user                createDB()
        5. Check table existance                checkTable()
        6. Create table                         createTable()
    """
    def __init__(self, email):
        self.email = email.lower()
        self.dbname = self.email.split("@")[0]

    def registered(self):
        # Checks if the user if registered or not.
        command1 = "USE userinformation"
        command2 = f"SELECT dbname FROM users WHERE dbname = '{self.dbname}'"
        try:
            cursor.execute(command1)
            cursor.execute(command2)
            if cursor.fetchall() == []:
                return False
            else:
                return True
        except mysql.Error as err:
            writeErrLog(str(err))
            return 132

    def newUser(self, name, institute, region):
        # Creates new user.
        command1 = "USE userinformation"
        command2 = f"INSERT INTO users (dbname, name, email, institute, region) VALUES ('{self.dbname}', '{name}', '{self.email}', '{institute}', '{region}')"
        try:
            cursor.execute(command1)
            cursor.execute(command2)
            myConn.commit()
        except mysql.Error as err:
            writeErrLog(str(err))
            return 132
        
    def useDB(self):
        # To check if user's db exists.
        checkDB = f"SHOW DATABASES LIKE '{self.dbname}'"
        try:
            cursor.execute(checkDB)  # Check DB
        except mysql.Error as err:
            return 132
        if cursor.fetchone() is not None:
            try:
                cursor.execute(f"USE {self.dbname}")  # Use DB
            except mysql.Error as err:
                writeErrLog(str(err))
                return 132
            return 1
        return 0
    
    def createDB(self):
        # To create db for user.
        createDB = f"CREATE DATABASE {self.dbname}"
        try:
            cursor.execute(createDB)
            myConn.commit()
            cursor.execute(f"USE {self.dbname}")
        except mysql.Error as err:
            writeErrLog(str(err))
            return 132
        
    def checkTable(self, tableName=TABLENAME):
        # To create table for each month.
        checkTable = f"SHOW TABLES LIKE '{tableName}'"
        try:
            cursor.execute(checkTable)
        except mysql.Error as err:
            writeErrLog(str(err))
            return 132
        return cursor.fetchone() is not None

    def createTable(self):
        # To create table.
        ctbm = f"""
            CREATE TABLE {TABLENAME} (
                ename CHAR(120) NOT NULL,
                amount INT NOT NULL,
                category CHAR(120) NOT NULL,
                etime TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                edate DATE NOT NULL DEFAULT (CURRENT_DATE),
                description VARCHAR(120) NOT NULL
            )
        """
        try:
            cursor.execute(ctbm)
            myConn.commit()
        except mysql.Error as err:
            writeErrLog(str(err))
            return 132

def insertRec(name, amount, category, time=None, date=None,description="Null"):
    # Insert records into table         insert(<name, amount, category>, [time, date, description])

    if not time and not date:
        cam1 = f"INSERT INTO {TABLENAME} (ename, amount, category, etime, edate, description) VALUES (%s, %s, %s, CURRENT_TIMESTAMP, CURDATE(), %s)"
        try:
            cursor.execute(cam1, (name, amount, category, description))
            myConn.commit()
        except mysql.Error as err:
            writeErrLog(str(err))
            return 132
    elif not time and date:
        cam1 = f"INSERT INTO {TABLENAME} (ename, amount, category, etime, edate, description) VALUES (%s, %s, %s, CURRENT_TIMESTAMP, %s, %s)"
        try:
            cursor.execute(cam1, (name, amount, category, date, description))
            myConn.commit()
        except mysql.Error as err:
            writeErrLog(str(err))
            return 132
    else:
        cam1 = f"INSERT INTO {TABLENAME} (ename, amount, category, etime, edate, description) VALUES (%s, %s, %s, %s, %s, %s)"
        try:
            cursor.execute(cam1, (name, amount, category, time, date, description))
            myConn.commit()
        except mysql.Error as err:
            writeErrLog(str(err))
            return 132

def monthlyExpense(monthName):
    try:
        # Ensure monthName is a string
        if not isinstance(monthName, str):
            writeErrLog(str(err))
            return {"success": False, "error": f"Invalid type: expected str, got {type(monthName).__name__}"}

        # Ensure minimum length to avoid indexing errors
        if len(monthName) < 7:
            writeErrLog(str(err))
            return {"success": False, "error": f"Invalid month format: too short ('{monthName}')"}
        
        # Validate expected format "mMM_YYYY"
        if not (monthName.startswith("m") and monthName[1:3].isdigit() and monthName[3] == "_" and monthName[4:].isdigit()):
            writeErrLog(str(err))
            return {"success": False, "error": f"Invalid format: expected 'mMM_YYYY', got '{monthName}'"}
        
        query1 = f"""
            SELECT ename, amount, category, etime, edate, description 
            FROM {monthName}
        """
 
        cursor.execute(query1)
        results = cursor.fetchall()

    except mysql.Error as err:
        writeErrLog(str(err))
        return {"success": False, "error": str(err)}

    # Convert results to DataFrame
    df = pd.DataFrame(results, columns=[column[0] for column in cursor.description])

    total_expenses = []  # To store final expense list

    for _, row in df.iterrows():
        # Store formatted expense
        total_expenses.append({
            "ename": row["ename"],
            "amount": row["amount"],
            "etime": row["etime"].strftime("%a, %d %b %Y %H:%M:%S GMT"),
            "edate": row["edate"].strftime("%a, %d %b %Y %H:%M:%S GMT"),
            "description": row["description"]
        })

    return {
        "success": True,
        "budget": 0,  # Set budget manually or fetch dynamically
        "totalExpense": total_expenses,
    }

class RI:
    def month(self, email, month):
        user = General(email)
        db_exists = user.useDB()
        if db_exists == 0:
            # No database, return empty data
            return {
                "success": True,
                "transactions": []
            }
        
        # Check if table exists for the month
        if not user.checkTable(month):
            # No table for this month, return empty data
            return {
                "success": True,
                "transactions": []
            }
        
        try:
            print()
            cursor.execute(f"SELECT * FROM {month}")
            data = cursor.fetchall()
            columns = [col[0] for col in cursor.description]
            rows = [dict(zip(columns, row)) for row in data]
            return rows

        except mysql.Error as err:
            writeErrLog(str(err))
            return
=======
import mysql.connector.pooling
from datetime import date, datetime, timedelta
from random import randint
from config import DB_CONFIG

def writeErrLog(msg):
    """Log errors to the error log file."""
    with open("log/err.log", "a") as file_object:
        file_object.write(msg + "\n\n")

# Create a connection pool for database connections
db_config = DB_CONFIG

connection_pool = mysql.connector.pooling.MySQLConnectionPool(pool_name="mypool",
                                                              pool_size=5,
                                                              **db_config)

def get_db_connection():
    """Get a connection from the connection pool."""
    return connection_pool.get_connection()

def otp_generate(email):
    """
    Generate an OTP for the given email and store it in the database.

    Args:
        email (str): The email address to generate the OTP for.

    Returns:
        tuple: A status message and the generated OTP.
    """
    otp = str(randint(100000, 999999))  # Generate a 6-digit OTP
    expiration_time = datetime.now() + timedelta(minutes=10)  # OTP expires in 10 minutes

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            REPLACE INTO user_otp(email, otp, expiration_time) 
            VALUES(%s, %s, %s)
        """, (email, otp, expiration_time))
        conn.commit()
        return "OTP:GENERATED", otp
    except mysql.connector.Error as err:
        writeErrLog(f"Error generating OTP for email {email}: {err}")
        return {'success': False, 'err': str(err)}
    finally:
        cursor.close()
        conn.close()

def otp_verify(email, otp):
    """
    Verify the OTP for the given email.

    Args:
        email (str): The email address to verify the OTP for.
        otp (str): The OTP to verify.

    Returns:
        tuple: A success status and a verification result (1 for success, 0 for failure).
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT otp, expiration_time 
            FROM user_otp 
            WHERE email = %s
        """, (email,))
        result = cursor.fetchone()

        if result:
            if str(result['otp']) == otp:
                if datetime.now() <= result['expiration_time']:
                    cursor.execute("DELETE FROM user_otp WHERE email = %s", (email,))
                    conn.commit()
                    return {'success': True}, 1
                else:
                    return {'success': False, 'error': 'OTP expired'}, 0
            else:
                return {'success': False, 'error': 'Invalid OTP'}, 0
        else:
            return {'success': False, 'error': 'No OTP found'}, 0
    except mysql.connector.Error as err:
        writeErrLog(f"Error verifying OTP for email {email}: {err}")
        return {'success': False, 'error': str(err)}
    finally:
        cursor.close()
        conn.close()

def table_name_generate(email, month=None, year=None):
    """
    Generate a table name based on the email and the specified or current month/year.

    Args:
        email (str): The email address to base the table name on.
        month (int, optional): The month (1-12) for the table name. Defaults to the current month.
        year (int, optional): The year for the table name. Defaults to the current year.

    Returns:
        str: The generated table name.
    """
    # Validate email format
    if '@' not in email:
        raise ValueError("Invalid email format")

    # Extract the username from the email
    username = email.split('@')[0]

    # Get the current month and year if not provided
    today = date.today()
    month = month or today.month
    year = year or today.year

    # Validate month range
    if month < 1 or month > 12:
        raise ValueError("Month must be between 1 and 12")

    # Format the month as mXX (e.g., m03 for March)
    formatted_month = f"m{month:02d}"

    # Construct the table name
    table_name = f"{username}_{formatted_month}_{year}"
    return table_name

def create_table(table_name):
    """
    Create a table in the database.

    Args:
        table_name (str): Name of the table to create.
    """
    create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            ename VARCHAR(120) NOT NULL,
            amount INT NOT NULL,
            category VARCHAR(120) NOT NULL,
            etime TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            edate DATE NOT NULL,
            description VARCHAR(120) NOT NULL
        )
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(create_table_query)
        conn.commit()
        return {"success": True, "message": "Table created successfully"}
    except mysql.connector.Error as err:
        writeErrLog(f"Error creating table '{table_name}': {err}")
        return {"success": False, "message": f"Error creating table: {err}"}
    finally:
        cursor.close()
        conn.close()

class General:
    def __init__(self, email):
        """
        Initialize the General class with the user's email.

        Args:
            email (str): The email address of the user.
        """
        self.email = email.lower()
        self.username = self.email.split("@")[0]  # Derive username from email

    def registered(self):
        """
        Check if the user is registered in the user_information table.

        Returns:
            bool: True if the user is registered, False otherwise.
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM user_information WHERE email = %s", (self.email,))
            result = cursor.fetchone()
            if result:
                return True
            else:
                return False
        except mysql.connector.Error as err:
            writeErrLog(f"Error checking registration for email {self.email}: {err}")
            return False
        finally:
            cursor.close()
            conn.close()

    def new_user(self, name, institute, region):
        """
        Create a new user in the user_information table and create the current month's table.

        Args:
            name (str): The full name of the user.
            institute (str): The institute or organization of the user.
            region (str): The region of the user.

        Returns:
            dict: A dictionary containing the success status and a message.
        """
        command = """
            INSERT INTO user_information (username, name, email, institute, region)
            VALUES (%s, %s, %s, %s, %s)
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Insert the new user into the user_information table
            cursor.execute(command, (self.username, name, self.email, institute, region))
            conn.commit()

            # Generate the table name for the current month
            table_name = table_name_generate(self.email)

            # Create the current month's table for the user
            create_table_result = create_table(table_name)
            if not create_table_result.get("success"):
                writeErrLog(f"Error creating table for user {self.username}: {create_table_result.get('message')}")
                return {"success": False, "message": "User created, but failed to create monthly table"}

            return {"success": True, "message": "User created successfully and monthly table created"}
        except mysql.connector.Error as err:
            writeErrLog(f"Error creating new user with email {self.email}: {err}")
            return {"success": False, "message": f"Error creating user: {err}"}
        finally:
            cursor.close()
            conn.close()

def getTotalSpent(tableName=None, email=None):
    """
    Calculate the total amount spent by a user.

    Args:
        tableName (str, optional): The name of the table to query. Defaults to None.
        email (str, optional): The email address of the user. Defaults to None.

    Returns:
        dict: A dictionary containing the success status and the total amount spent.
    """
    try:
        # Generate the table name for the current month if not provided
        table_name = tableName or table_name_generate(email)

        # Check if the table exists
        check_table_query = f"SHOW TABLES LIKE '{table_name}'"
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(check_table_query)
        table_exists = cursor.fetchone()

        if not table_exists:
            return {"success": True, "totalExpense": 0}

        # SQL query to calculate the total amount
        query = f"SELECT SUM(amount) AS total_spent FROM {table_name}"
        cursor.execute(query)
        result = cursor.fetchone()

        # If no expenses are found, return 0
        total_spent = result[0] if result[0] is not None else 0
        return {"success": True, "totalExpense": total_spent}
    except mysql.connector.Error as err:
        writeErrLog(f"Error calculating total spent for user {email}: {err}")
        return {"success": False, "message": f"Error calculating total spent: {err}"}
    finally:
        cursor.close()
        conn.close()

def transactions(email=None, fullTable=None):
    """
    Retrieve all transactions for a specific month from the user's table.

    Args:
        email (str): The email address of the user.
        month (int, optional): The month (1-12) to filter transactions. Defaults to the current month.
        year (int, optional): The year to filter transactions. Defaults to the current year.

    Returns:
        dict: A dictionary containing the success status and the list of transactions.
    """
    try:
        # Generate the table name for the specified or current month
        table_name = fullTable or (table_name_generate(email))
        # Check if the table exists
        check_table_query = f"SHOW TABLES LIKE '{table_name}'"
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(check_table_query)
        table_exists = cursor.fetchone()

        if not table_exists:
            return {"success": True, "transactions": []}

        # SQL query to retrieve all transactions
        query = f"SELECT ename, amount, category, etime, edate, description FROM {table_name}"
        cursor.execute(query)
        transactions = cursor.fetchall()

        return {"success": True, "transactions": transactions}
    except mysql.connector.Error as err:
        writeErrLog(f"Error retrieving transactions for user {email}: {err}")
        return {"success": False, "message": f"Error retrieving transactions: {err}"}
    finally:
        cursor.close()
        conn.close()

def writeExpense(email, ename, amount, category, edate, description):
    """
    Insert an expense into the user's respective table. If the table does not exist, create it.

    Args:
        email (str): The email address of the user.
        ename (str): The name of the expense.
        amount (int): The amount of the expense.
        category (str): The category of the expense.
        edate (str): The date of the expense (format: YYYY-MM-DD).
        description (str): A description of the expense.

    Returns:
        dict: A dictionary containing the success status and a message.
    """
    try:
        # Extract the month and year from the provided date
        expense_date = datetime.strptime(edate, "%Y-%m-%d")
        month = expense_date.month
        year = expense_date.year

        # Generate the table name based on the email and the expense date
        table_name = table_name_generate(email, month)

        # Check if the table exists
        check_table_query = f"SHOW TABLES LIKE '{table_name}'"
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(check_table_query)
        table_exists = cursor.fetchone()

        # If the table does not exist, create it
        if not table_exists:
            create_table_result = create_table(table_name)
            if not create_table_result.get("success"):
                writeErrLog(f"Error creating table '{table_name}' for user {email}: {create_table_result.get('message')}")
                return {"success": False, "message": f"Error creating table: {create_table_result.get('message')}"}

        # Insert the expense into the table
        insert_query = f"""
            INSERT INTO {table_name} (ename, amount, category, edate, description)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (ename, amount, category, edate, description))
        conn.commit()

        return {"success": True, "message": "Expense added successfully"}
    except mysql.connector.Error as err:
        writeErrLog(f"Error inserting expense for user {email}: {err}")
        return {"success": False, "message": f"Error inserting expense: {err}"}
    finally:
        cursor.close()
        conn.close()

def user_name(email):
    """
    Retrieve the name of a user from the user_information table using their email.

    Args:
        email (str): The email address of the user.

    Returns:
        dict: A dictionary containing the success status and the user's name, or an error message.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Query to fetch the user's name
        query = "SELECT name FROM user_information WHERE email = %s"
        cursor.execute(query, (email,))
        result = cursor.fetchone()

        if result:
            return {"success": True, "name": result['name']}
        else:
            return {"success": False, "message": "User not found"}
    except mysql.connector.Error as err:
        writeErrLog(f"Error retrieving name for email {email}: {err}")
        return {"success": False, "message": f"Error retrieving name: {err}"}
    finally:
        cursor.close()
        conn.close()

def get_card_data(email, month, year):
    """
    Fetch card information for the given email, month, and year.

    Args:
        email (str): The email address of the user.
        month (int): The month for which data is requested.
        year (int): The year for which data is requested.

    Returns:
        dict: A dictionary containing the success status and card data.
    """
    try:
        table_name = table_name_generate(email, month, year)  # Generate table name dynamically
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Check if the table exists
        check_table_query = f"SHOW TABLES LIKE '{table_name}'"
        cursor.execute(check_table_query)
        table_exists = cursor.fetchone()

        if not table_exists:
            # If the table does not exist, return default values
            return {
                "success": True,
                "data": {
                    "total_spent": 0,
                    "transaction_count": 0,
                    "most_spent_category": "None",
                    "most_spent_amount": 0,
                }
            }

        # Query to fetch total spent, average per day, and transaction count
        main_query = f"""
            SELECT 
                SUM(amount) AS total_spent,
                COUNT(*) AS transaction_count
            FROM {table_name}
        """
        cursor.execute(main_query)
        main_result = cursor.fetchone()

        # Query to fetch the most spent category and its total amount
        category_query = f"""
            SELECT 
                category AS most_spent_category,
                SUM(amount) AS most_spent_amount
            FROM {table_name}
            GROUP BY category
            ORDER BY SUM(amount) DESC
            LIMIT 1
        """
        cursor.execute(category_query)
        category_result = cursor.fetchone()

        # Combine results
        return {
            "success": True,
            "data": {
                "total_spent": main_result["total_spent"] or 0,
                "transaction_count": main_result["transaction_count"] or 0,
                "most_spent_category": category_result["most_spent_category"] if category_result else "None",
                "most_spent_amount": category_result["most_spent_amount"] if category_result else 0,
            }
        }
    except mysql.connector.Error as err:
        writeErrLog(f"Error fetching card data for {email}: {err}")
        return {"success": False, "message": f"Error fetching card data: {err}"}
    finally:
        cursor.close()
        conn.close()

def deleteExpense(email, name, date):
    """
    Delete an expense record from the user's table based on the name and date.

    Args:
        email (str): The email address of the user.
        name (str): The name of the expense to delete.
        date (str): The date of the expense (format: YYYY-MM-DD).

    Returns:
        dict: A dictionary containing the success status and a message.
    """
    try:
        # Extract the month and year from the provided date
        expense_date = datetime.strptime(date, "%Y-%m-%d")
        month = expense_date.month
        year = expense_date.year

        # Generate the table name based on the email and the expense date
        table_name = table_name_generate(email, month, year)

        # Check if the table exists
        check_table_query = f"SHOW TABLES LIKE '{table_name}'"
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(check_table_query)
        table_exists = cursor.fetchone()

        if not table_exists:
            return {"success": False, "message": "Table does not exist"}

        # Delete the record from the table
        delete_query = f"""
            DELETE FROM {table_name}
            WHERE ename = %s AND edate = %s
        """
        cursor.execute(delete_query, (name, date))
        conn.commit()

        if cursor.rowcount > 0:
            return {"success": True, "message": "Expense deleted successfully"}
        else:
            return {"success": False, "message": "No matching record found"}
    except mysql.connector.Error as err:
        writeErrLog(f"Error deleting expense '{name}' on '{date}' for user {email}: {err}")
        return {"success": False, "message": f"Error deleting expense: {err}"}
    finally:
        cursor.close()
        conn.close()

"""
DATABASE

TABLE : user_otp
PRE-DEFINED : True
SCHEMA : 
    #    Name	            Type            Null	Default
    1    email  Primary	    varchar(200)    No      None
    2    otp	            varchar(64)     No	    None
    3    expiration_time	datetime        No	    None

TABLE : user_information
PRE-DEFINED : True
SCHEMA :
    #   Name                    Type            Null    Default
    1   username    Primary     varchar(120)    No      None
    2   name                    varchar(120)    No      None
    3   email                   varchar(200)    No      None
    4   institute               varchar(200)    No      None
    5   region                  varchar(120)    No      None

TABLE : <username>_category (yet to code)
PRE-DEFINED : False
SCHEMA :
    #   Name        Type            Null    Default
    1   Category    varchar(120)    No      None

TABLE : <username>_m<month>_<year>
PRE-DEFINED : False
SCHEMA : 
    #	Name	    Type	        Null	Default
    1	ename	    CHAR(120)	    No	    None
    2	amount	    INT	            No	    None
    3	category	CHAR(120)	    No	    None
    4	etime	    TIMESTAMP	    No	    CURRENT_TIMESTAMP
    5	edate	    DATE	        No	    CURRENT_DATE
    6	description	VARCHAR(120)	No	    None

"""
>>>>>>> recover-local
