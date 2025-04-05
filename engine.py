import mysql.connector.pooling
from datetime import date, datetime, timedelta
from random import randint

def writeErrLog(msg):
    """Log errors to the error log file."""
    with open("log/err.log", "a") as file_object:
        file_object.write(msg + "\n\n")

# Create a connection pool for database connections
db_config = {
    'user': 'sql12771396',
    'password': 'IKVG5irB59',
    'host': 'sql12.freesqldatabase.com',
    'database': 'sql12771396'
}
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