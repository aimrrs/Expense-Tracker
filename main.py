import mysql.connector as mysql
from datetime import date
from config import USERNAME, PASSWORD
from mysql.connector import errorcode

print("[ EXPENSE-TRACKER ] Starting...")

# Getting username and password.
USERNAME = USERNAME
PASSWD = PASSWORD

# Getting the 'D, M, Y' of current day.
td = date.today()

# Creating instance for connection.
myConn = mysql.connect(user=USERNAME, password=PASSWD, host="localhost")
cursor = myConn.cursor()
print("[ EXPENSE-TRACKER ] Connection successfully created.")

def createDatabase():
    # To create base database, if not exists.
    checkDB = "SHOW DATABASES LIKE 'expense'"
    createDB = "CREATE DATABASE expense"
    try:
        cursor.execute(checkDB) # Check DB
    except mysql.connector.Error as err:
            print(err)
    if cursor.fetchone() is None:
        try:
            cursor.execute(createDB) # Create DB
            myConn.commit()
            print("[ EXPENSE-TRACKER ] Base database created.")
        except mysql.connector.Error as err:
            print(err)
    else:
        print("[ EXPENSE-TRACKER ] Base database already exists.")
        try:
            cursor.execute("USE expense") # Use DB
            print("[ EXPENSE-TRACKER ] Base database in use.")
        except mysql.connector.Error as err:
            print(err)

def Table():
    # Creating table by month, if not exists.
    M, Y = td.month, td.year
    if len(str(M)) == 1:
        tableName = f'0{M}_{Y}'
    else:
        tableName = f'{M}_{Y}'
    checkTable = f"SHOW TABLES LIKE '{tableName}'"
    try:
        cursor.execute(checkTable)
    except mysql.connector.Error as err:
            print(err)
    if cursor.fetchone() is not None:
        print(f"[ EXPENSE-TRACKER] Month 0{M} table already exists.")
    else:
        ctbm = f"""
        CREATE TABLE {tableName} (
            category CHAR(120) NOT NULL,
            value INT NOT NULL,
            time time,
            edate CHAR(10) NOT NULL,
            description VARCHAR(120) NOT NULL
        )
        """
        try:
            cursor.execute(ctbm)
            myConn.commit()
            print(f"[ EXPENSE-TRACKER] Month {M} table created.")
        except mysql.connector.Error as err:
            print(err)

class RI:
    # To get the expense data to user as information.
    def __init__ (self):
        pass

    def month(self, monthYear):
        # RI as month.
        pass

    def week(self, weekMonthYear):
        # RI as week.
        pass

    def day(self, today):
        # RI as day - date.
        pass

    def ranrange(self, start, end):
        # RI with a range.
        pass