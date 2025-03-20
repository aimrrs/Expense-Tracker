from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from engine import Otp

app = Flask(__name__)
CORS(app)
userLogin = Otp()

otp_storage = {}

@app.route("/send-otp", methods=['POST'])
def snd_otp():
    data = request.json
    email = data.get('email')
    if not email:
        return jsonify({"success": False, "message": "Email is required"}), 400
    try:
        otp = userLogin.generate_otp()
        otp_storage[email] = otp
        userLogin.send_otp(email)
        return jsonify({"success": True, "message": "OTP sent successfully"})
    except Exception as err:
        return jsonify({"success": False, "message": str(err)}), 500

@app.route("/verify-otp", methods=['POST'])
def verify_otp():
    data = request.json
    email = data.get('email')
    otp = data.get('otp')
    if not email or not otp_storage:
        return jsonify({"success": False, "message": "Email and OTP are required"}), 400
    
    if email in otp_storage and otp_storage[email] == otp:
        del otp_storage[email]
        return jsonify({"success": True, "message": "Login successful"})
    else:
        return jsonify({"success": False, "message": "Invalid OTP"}), 400

@app.route("/login")
def login():
    return render_template("login.html")


if __name__ == "__main__":
    app.run(debug=True,
            host='0.0.0.0',
            port='8080')