import main
import csv

user1 = main.General("aimrrs404gmailcom")
if not user1.checkDB():
    user1.createDB()
    print(0)
if not user1.checkTable():
    user1.createTable()



with open("expenses_dataset.csv", "r") as file_object:
    rows = csv.reader(file_object)
    for row in rows:
        main.Gi.insert(row[0], row[1], row[2], row[3], row[4], row[5])


"""
User opens the website
User logins with their email ID
"""