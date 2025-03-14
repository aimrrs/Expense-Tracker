from engine import General, Otp

if __name__ == "__main__":
    userEmail = input("Enter email: ")

    userGen = General(userEmail)
    if userGen.registered():
        userOtp = Otp()
        userOtp.generate_otp()
        userOtp.send_otp(userEmail)
        userSentOtp = input("Enter otp: ")
        if userOtp.validate_otp(userSentOtp):
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
