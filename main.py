import mysql.connector as mysql
from datetime import date
import config
from mysql.connector import errorcode
from calendar import month_name
import random
import smtplib

# Getting username and password.
USERNAME = config.DB_USERNAME
PASSWD = config.DB_PASSWORD

# Getting the 'D, M, Y' of current day.
td = date.today()
M, Y = td.month, td.year

if len(str(M)) == 1:
    TABLENAME = f"m0{M}_{Y}"
else:
    TABLENAME = f"m{M}_{Y}"

# Creating instance for connection.
myConn = mysql.connect(user=USERNAME, password=PASSWD, host="localhost")
cursor = myConn.cursor()

class Otp:
    def __init__(self):
        self.otpNumber = ""

    def generate_otp(self):
        for _ in range(5):
            self.otpNumber += str(random.randint(0, 9))

    def validate_otp(self, userOtp):
        return userOtp == self.otpNumber
    
    def send_otp(self, email):
        S = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        S.login(config.EMAIL_USERNAME, config.EMAIL_PASSWORD)
        S.sendmail(config.EMAIL_USERNAME, email, self.otpNumber)
        S.quit()

class General:
    def __init__(self, email):
        self.email = email.lower()

    def checkDB(self):
        checkDB = f"SHOW DATABASES LIKE '{self.email}'"
        try:
            cursor.execute(checkDB)  # Check DB
        except mysql.Error as err:
            print(err)
        if cursor.fetchone() is not None:
            try:
                cursor.execute(f"USE {self.email}")  # Use DB
            except mysql.Error as err:
                print(err)
            return 1
        return 0

    def createDB(self):
        createDB = f"CREATE DATABASE {self.email}"
        try:
            cursor.execute(createDB)
            myConn.commit()
            cursor.execute(f"USE {self.email}")
        except mysql.Error as err:
            print(err)

    def checkTable():
        checkTable = f"SHOW TABLES LIKE '{TABLENAME}'"
        try:
            cursor.execute(checkTable)
        except mysql.Error as err:
            print(err)
        return cursor.fetchone() is not None

    def createTable():
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
            print(err)

    def registered(self):
        command1 = "USE userinformation"
        command2 = f"SELECT email FROM user WHERE email = '{self.email.lower()}'"
        try:
            cursor.execute(command1)
            cursor.execute(command2)
            if cursor.fetchall() == []:
                return False
            else:
                return True
        except mysql.Error as err:
            print(err)

    def newUser(self, name, region):
        command1 = "USE userinformation"
        command2 = f"INSERT INTO user (email, name, region) VALUES ('{self.email}', '{name}', '{region}')"
        try:
            cursor.execute(command1)
            cursor.execute(command2)
            myConn.commit()
        except mysql.Error as err:
            print(err)

class Gi:
    def insert(name, amount, category, description="Null"):
        cam1 = f"INSERT INTO {TABLENAME} (ename, amount, category, etime, edate, description) VALUES (%s, %s, %s, CURRENT_TIMESTAMP, CURDATE(), %s)"
        try:
            cursor.execute(cam1, (name, amount, category, description))
            myConn.commit()
        except mysql.Error as err:
            print(err)

"""class RI:
    # To get the expense data to user as information.
    def __init__ (self):
        self.RI_data = {'record' : 0} # Contains RI return data, record 0 if not expense.

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

    def week(self, monthYear):
        # RI as week.
        # week from the same month, i.e. from same table.
        DWN = td.weekday()
        F = 7 - DWN
        P = 7 - (F + 1)

        tempname = TABLENAME.replace("_", "-")[::-1]
        command = f"SELECT * FROM {TABLENAME} WHERE edate BETWEEN {tempname}{F} AND {tempname}{P}"
        try:
            cursor.execute(command)
        except mysql.connector.Error as err:
            print(err)
        
        if cursor.fetchone() is None:
            self.RI_data["record"] = 0
            return self.RI_data
        
        self.RI_data["record"] = 1
        self.RI_data["weekExpense"] = cursor.fetchall()
        return self.RI_data

    def day(self, today):
        # RI as day - date.
        command = f"SELECT * FROM {TABLENAME} WHERE date = {today}"
        try:
            cursor.execute(command)
        except mysql.connector.Error as err:
            print(err)
        
        if cursor.fetchone() is None:
            self.RI_data["record"] = 0
            return self.RI_data
        
        self.RI_data["record"] = 1
        self.RI_data["todayExpense"] = cursor.fetchall()
        return self.RI_data

    def ranrange(self, start, end):
        # RI with a range.
        # Range must be from the same table i.e. from same month.
        command = f"SELECT * FROM {TABLENAME} WHERE edate BETWEEN {start} AND {end}"
        try:
            cursor.execute(command)
        except mysql.connector.Error as err:
            print(err)

        if cursor.fetchone() is None:
            self.RI_data["record"] = 0
            return self.RI_data
        
        self.RI_data["record"], self.RI_data["weekExpense"] = 1, cursor.fetchall()
        return self.RI_data
"""