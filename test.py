import mysql.connector as mysql
mycon = mysql.connect(user="root",passwd= "12345", host="localhost")
cursor = mycon.cursor()
cursor.execute("USE SAKILA")
cursor.execute("show tables")
ex1 = cursor.fetchall()
print(ex1)
for i in range(0,len(ex1)):
    for j in range(0,1):
         print(ex1[i][j])
