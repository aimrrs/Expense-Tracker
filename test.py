from main import General

user1 = General("23CU0310320@student.hindustanuniv.ac.in")

if user1.registered():
    print("Welcome back")
else:
    user1.newUser("Sriram", "Padur, Chennai, TamilNadu")