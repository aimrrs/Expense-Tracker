import mysql.connector as mysql
from datetime import date
import config
from calendar import month_name

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



class RI:
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
DATABASE STRUCTURE
Default Databases - userinformation
                    Table - users :
                            dbname char(120) PRIMARY KEY,
                            name char(120) NOT NULL,
                            email char(200) NOT NULL,
                            institute char(200) NOT NULL,
                            region char(120) NOT NULL)
"""