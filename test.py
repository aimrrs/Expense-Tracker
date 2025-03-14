from engine import General, Otp, insertRec
import csv

if __name__ == "__main__":
    userEmail = input("Enter email: ")

    userGen = General(userEmail)
    if userGen.registered():
        userOtp = Otp()
        userOtp.generate_otp()
        userOtp.send_otp(userEmail)
        userSentOtp = input("Enter otp: ")
        if userOtp.validate_otp(userSentOtp):
            if not userGen.useDB():
                userGen.createDB()
            print("Logined in successfully, User already registered.")
        else:
            print("Wrong OTP!")
    else:
        userOtp = Otp()
        userOtp.generate_otp()
        userOtp.send_otp(userEmail)
        userSentOtp = input("Enter otp: ")
        if userOtp.validate_otp(userSentOtp):
            print("New User, enter details for profile creation.")
            a = input("Enter name: ")
            b = input("Enter institute: ")
            c = input("Enter region: ")
            userGen.newUser(a, b, c)
            userGen.createDB()
            print("Logined in successfully, New user registered.")
        else:
            print("Wrong OTP!")

    if not userGen.checkTable():
        userGen.createTable()

    with open("expenses_dataset_v2.csv", "r") as file_object:
        rows = csv.reader(file_object)
        for row in rows:
            insertRec(row[0], row[1], row[2], row[3], row[4], row[5])