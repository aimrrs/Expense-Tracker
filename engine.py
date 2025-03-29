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
myConn = mysql.connect(user=USERNAME, password=PASSWD, host="localhost")
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
        
    def checkTable(self):
        # To create table for each month.
        checkTable = f"SHOW TABLES LIKE '{TABLENAME}'"
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

        # Extract month number safely
        month_num = int(monthName[1:3])  

        query = f"""
            SELECT ename, amount, category, etime, edate, description 
            FROM {monthName}
            WHERE MONTH(edate) = %s
        """
        cursor.execute(query, (month_num,))
        results = cursor.fetchall()

    except mysql.Error as err:
        writeErrLog(str(err))
        return {"success": False, "error": str(err)}

    except ValueError as e:
        writeErrLog(str(err))
        return {"success": False, "error": f"Month extraction failed: {str(e)}"}

    except Exception as e:
        writeErrLog(str(err))
        return {"success": False, "error": f"Unexpected error: {str(e)}"}

    # Convert results to DataFrame
    df = pd.DataFrame(results, columns=[column[0] for column in cursor.description])

    # Initialize category breakdown and daily expenses
    categoryBreakdown = {}
    dailyExpenses = {str(i): 0 for i in range(1, 32)}

    total_expenses = []  # To store final expense list

    for _, row in df.iterrows():
        edate = row["edate"]
        day = str(edate.day)  # Extract day from date

        # Update daily expenses
        dailyExpenses[day] += row["amount"]

        # Update category breakdown
        category = row["category"]
        categoryBreakdown[category] = categoryBreakdown.get(category, 0) + row["amount"]

        # Store formatted expense
        total_expenses.append({
            "ename": row["ename"],
            "amount": row["amount"],
            "category": category,
            "etime": row["etime"].strftime("%a, %d %b %Y %H:%M:%S GMT"),
            "edate": row["edate"].strftime("%a, %d %b %Y %H:%M:%S GMT"),
            "description": row["description"]
        })

    return {
        "success": True,
        "budget": 1200,  # Set budget manually or fetch dynamically
        "totalExpense": total_expenses,
        "categoryBreakdown": categoryBreakdown,
        "dailyExpenses": dailyExpenses
    }
