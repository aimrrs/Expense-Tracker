from main import General, Otp

user1 = General("aimrrs404@gmail.com")
otp = Otp()

if user1.registered():
    otp.generate_otp()
    otp.send_otp("aimrrs404@gmail.com")
    userOTP = input("Enter OTP : ")
    if otp.validate_otp(userOTP):
        print("Welcome back")
    else:
        print("Wrong OTP")
else:  
    otp.generate_otp()
    otp.send_otp("aimrrs404@gmail.com")
    userOTP = input("Enter OTP : ")
    if otp.validate_otp(userOTP):
        user1.newUser("Aimrrs", "Pondicherry")
    else:
        print("Wrong OTP")