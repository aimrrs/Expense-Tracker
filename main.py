import mysql.connector as mysql
from datetime import date
from config import USERNAME, PASSWORD
from mysql.connector import errorcode
from calendar import month_name

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
        print(f"[ EXPENSE-TRACKER ] Month 0{M} table already exists.")
    else:
        ctbm = f"""
        CREATE TABLE {tableName} (
            category CHAR(120) NOT NULL,
            value INT NOT NULL,
            time time,
            edate date NOT NULL,
            description VARCHAR(120) NOT NULL
        )
        """
        try:
            cursor.execute(ctbm)
            myConn.commit()
            print(f"[ EXPENSE-TRACKER ] Month {M} table created.")
        except mysql.connector.Error as err:
            print(err)

class RI:
    # To get the expense data to user as information.
    def __init__ (self):
        self.RI_data = {} # Contains RI return data.

    def month(self, monthYear):
        # RI as month.
        checkTablemonth = f"SHOW TABLES LIKE '{monthYear}'"
        try:
            cursor.excute(checkTablemonth)
        except mysql.connector.Error as err:
            print(err)
        if cursor.fetchone() is None:
            return "[ EXPENSE-TRACKER ] ERROR: Table does not exist."

        # Retrival of total expense from the table.   
        ctbm1 = f"SELECT SUM(VALUE) FROM {monthYear} AS Total_Expense"
        try:
            cursor.execute(ctbm1)
            r1 = cursor.fetchone()
        except mysql.connector.Error as err:
            print(err)
        
        # Retrival of total expense from each category 
        ctbm2 = f"SELECT DISTINCT(CATEGORY),SUM(VALUES) FROM {monthYear} AS CATEGORY , EXPENSE"
        try:
            cursor.execute(ctbm2)
            r2 = cursor.fetchall()
        except mysql.connector.Error as err:
            print(err)

        # Retrival of Average Expense of a day 
        ctbm3 = f"SELECT AVG(VALUE) FROM {monthYear} AS AVERAGE_EXPENSE"
        try:
            cursor.execute(ctbm3)
            r3 = cursor.fetchone()
        except mysql.connector.Error as err:
            print(err)
 
        # Retrival of details of the month
        temp1 = {"monthName":month_name[str(monthYear)],
                 "monthNumber":str({monthYear}[0:2]),
                 "year":{monthYear}[3:]}
        self.RI_data.update(temp1)
        self.RI_data.update({"totalExpense":r1,"expenseInEachCat":r2,"avgExp":r3})
        
        return self.RI_data         

    def week(self, weekMonthYear):
        # RI as week.
        pass

    def day(self, today):
        # RI as day - date.
        pass

    def ranrange(self, start, end):
        # RI with a range.
        pass
    