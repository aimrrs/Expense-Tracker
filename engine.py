import smtplib
import random
import config
from email.message import EmailMessage
import mysql.connector as mysql
from datetime import date

def writeErrLog(msg):
    with open("log/err.log", "a") as file_object:
        file_object.write(msg+"\n\n")

class Otp:
    """
    To generate otp,
        1. Declare class    Otp()
        2. Generate opt     generate_otp()
        3. send otp         send_otp(<to_email>)
        4. validate otp     validate_otp()
    """
    def __init__(self):
        self.otpNumber = "" # otp
        self.msg = EmailMessage()
        self.msg['Subject'] = "Your OTP for Secure Login - Expense Tracker"
        self.msg['From'] = config.EMAIL_USERNAME

    def generate_otp(self):
        # Generates otp.
        for _ in range(5):
            self.otpNumber += str(random.randint(0, 9))

    def validate_otp(self, userOtp):
        # Validates user otp to system otp.
        return userOtp == self.otpNumber
    
    def send_otp(self, email):
        # Sends otp through mail.
        self.msg['To'] = email
        self.msg.set_content(f"Dear User,\n\nYour One-Time Password (OTP) for logging into your Expense Tracker account is:\n\n{self.otpNumber}\n\nThis OTP is valid for 5 minutes. Please do not share it with anyone.\n\nStay on top of your expenses,\nExpense Tracker Team\n")
        S = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        S.login(config.EMAIL_USERNAME, config.EMAIL_PASSWORD)
        S.send_message(self.msg)
        S.quit()

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

class General:
    """
    General consists
        1. To check is user is registered       registered()
        2. To create new user profile           newUser(<name, institute, region>)
        3. To check if user db exists           checkDB()
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
        
    def checkDB(self):
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

def insert(name, amount, category, time=None, date=None,description="Null"):
    # Insert records into table         insert(<name, amount, category>, [time, date, description])

    if not time and not date:
        cam1 = f"INSERT INTO {TABLENAME} (ename, amount, category, etime, edate, description) VALUES (%s, %s, %s, CURRENT_TIMESTAMP, CURDATE(), %s)"
        try:
            cursor.execute(cam1, (name, amount, category, description))
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
