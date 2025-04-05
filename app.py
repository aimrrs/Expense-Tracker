from flask import Flask, request, jsonify, session, redirect, render_template
from flask_mail import Mail, Message
from engine import *
from datetime import datetime

app = Flask(__name__)
app.secret_key = "jkgigegegskeejghaelgjqgrueelkjglkjeougqeiuhebjg"

# Flask-Mail configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Replace with your SMTP server
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'noreplyforexpensetracker@gmail.com'  # Replace with your email
app.config['MAIL_PASSWORD'] = 'ieag xano eyay gefi'  # Replace with your email password

mail = Mail(app)

def send_mail(to_email, subject, body):
    """
    Send an email using Flask-Mail.

    Args:
        to_email (str): Recipient's email address.
        subject (str): Subject of the email.
        body (str): Body of the email.

    Returns:
        bool: True if the email was sent successfully, False otherwise.
    """
    try:
        msg = Message(subject=subject, sender=app.config['MAIL_USERNAME'], recipients=[to_email])
        msg.body = body
        mail.send(msg)
        return True
    except Exception as err:
        writeErrLog(f"Error sending email to {to_email}: {str(err)}")
        return False

@app.route("/send-otp", methods=['POST'])
def send_otp():
    """
    Endpoint to generate and send an OTP to the provided email.
    """
    data = request.json
    email = data.get('email')

    if not email:
        writeErrLog("Email is required but not provided.")
        return jsonify({"success": False, "message": "Email is required"}), 400

    try:
        otp_status, otp = otp_generate(email)
        if otp_status != "OTP:GENERATED":
            return jsonify({"success": False, "message": "Failed to generate OTP"}), 500

        # Send the OTP via email
        subject = "Your OTP for Secure Login - Expense Tracker"
        body = f"Dear User,\n\nYour One-Time Password (OTP) for logging into your Expense Tracker account is:\n\n{otp}\n\nThis OTP is valid for 10 minutes. Please do not share it with anyone.\n\nStay on top of your expenses,\nExpense Tracker Team\n"
        if send_mail(email, subject, body):
            return jsonify({"success": True, "message": "OTP sent successfully"})
        else:
            writeErrLog(f"Failed to send OTP email to {email}")
            return jsonify({"success": False, "message": "Failed to send OTP email"}), 500
    except Exception as err:
        writeErrLog(f"Error in /send-otp endpoint for email {email}: {str(err)}")
        return jsonify({"success": False, "message": "Failed to send OTP"}), 500

@app.route("/verify-otp", methods=['POST'])
def verify_otp():
    """
    Endpoint to verify the OTP for the provided email.
    """
    data = request.json
    email = data.get('email')
    otp = data.get('otp')

    if not email or not otp:
        writeErrLog("Email or OTP not provided for verification.")
        return jsonify({"success": False, "message": "Email and OTP are required"}), 400

    try:
        verification_result, status = otp_verify(email, otp)
        if status == 1:  # OTP verified successfully
            # Check if the user is registered
            user = General(email)
            is_registered = user.registered()

            if not is_registered:
                return jsonify({
                    "success": True,
                    "registered": False,
                    "message": "OTP verified. Please complete registration."
                })
            else:
                # User is registered, set session and return success
                session['email'] = email
                return jsonify({
                    "success": True,
                    "registered": True,
                    "message": "Login successful"
                })
        else:
            return jsonify({"success": False, "message": "Invalid OTP"}), 400
    except Exception as err:
        writeErrLog(f"Error in /verify-otp endpoint for email {email}: {str(err)}")
        return jsonify({"success": False, "message": "Failed to verify OTP"}), 500

@app.route("/register", methods=['POST'])
def register():
    """
    Endpoint to register a new user.
    """
    if 'email' in session:
        return redirect("/")

    data = request.json
    email = data.get('email')
    name = data.get('name')
    institute = data.get('institute')
    region = data.get('region')

    # Validate input fields
    if not email or not name or not institute or not region:
        writeErrLog("All fields are required for registration.")
        return jsonify({"success": False, "message": "All fields are required"}), 400

    try:
        user = General(email)

        # Check if the user is already registered
        if user.registered():
            return jsonify({"success": True, "message": "User is already registered"}), 200

        # Create a new user
        result = user.new_user(name, institute, region)
        if not result.get("success"):
            writeErrLog(f"Error creating user: {result.get('message')}")
            return jsonify({"success": False, "message": result.get("message")}), 500

        # Set session
        session['email'] = email
        return jsonify({"success": True, "message": "Registration successful"}), 200

    except Exception as err:
        writeErrLog(f"Error in /register endpoint for email {email}: {str(err)}")
        return jsonify({"success": False, "message": "An error occurred during registration"}), 500

@app.route("/login")
def login():
    if 'email' not in session:
        return render_template("login.html")
    else:
        return redirect("/")

@app.route("/logout")
def logout():
    session.pop('email', None)
    return redirect("/login")

@app.route("/")
def index():
    if 'email' not in session:
        return redirect("/login")
    return render_template("main.html")

@app.route("/api/transactions")
def transaction():
    if 'email' not in session:
        return jsonify({"success": False, "message": "Not authenticated"}), 401
    email = session['email']
    month = request.args.get('month', type=str)
    if not month:
        trans = transactions(email)
    else:
        x = email.split("@")[0] + '_' + month
        trans = transactions(fullTable=x)
    return jsonify(trans)

@app.route("/api/add-expense", methods=['POST'])
def add_expense():
    """
    Endpoint to add an expense for the authenticated user.
    """
    if 'email' not in session:
        return jsonify({"success": False, "message": "Not authenticated"}), 401

    data = request.json
    name = data.get('name')
    amount = data.get('amount')
    category = data.get('category')
    date_str = data.get('date')  # Expected format: YYYY-MM-DD
    description = data.get('description', 'Null')

    # Validate required fields
    if not name or not amount or not category or not date_str:
        return jsonify({"success": False, "message": "Missing required fields"}), 400

    try:
        # Insert the expense into the respective table
        result = writeExpense(
            email=session['email'],
            ename=name,
            amount=amount,
            category=category,
            edate=date_str,
            description=description
        )

        if not result.get("success"):
            return jsonify({"success": False, "message": result.get("message")}), 500

        return jsonify({"success": True, "message": "Expense added successfully"}), 200
    except Exception as err:
        writeErrLog(f"Error in /add-expense endpoint: {str(err)}")
        return jsonify({"success": False, "message": str(err)}), 500

@app.route('/api/user-info', methods=['GET'])
def user_info():
    if 'email' not in session:
        return jsonify({"success": False, "message": "Not authenticated"}), 401

    # Example user data (replace with actual database query)
    user = user_name(session['email'])
    return jsonify({"success": True, "user": user})

@app.route("/analytics")
def analytics():
    if 'email' not in session:
        redirect("/login")
    return render_template("analytics.html")

@app.route('/api/card-data', methods=['GET'])
def get_card_data_api():
    """
    API to fetch card information for the selected month and year.
    """
    if 'email' not in session:
        return jsonify({"success": False, "message": "Not authenticated"}), 401

    # Get month and year from query parameters
    month = request.args.get('month', default=datetime.now().month, type=int)
    year = request.args.get('year', default=datetime.now().year, type=int)

    # Fetch card data from the database
    result = get_card_data(email=session['email'], month=month, year=year)

    if result["success"]:
        return jsonify({"success": True, "cardData": result["data"]})
    else:
        return jsonify({"success": False, "message": result["message"]}), 500

@app.route("/api/delete-expense", methods=['DELETE'])
def delete_expense():
    """
    Endpoint to delete an expense for the authenticated user.

    Returns:
        JSON response indicating success or failure.
    """
    if 'email' not in session:
        return redirect('/login')

    data = request.json
    date = data.get('date')
    name = data.get('name')

    if not date or not name:
        return jsonify({"success": False, "message": "Missing required fields"}), 400

    # Validate date format
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return jsonify({"success": False, "message": "Invalid date format. Use YYYY-MM-DD."}), 400

    email = session['email']
    dt = deleteExpense(email, name, date)
    return jsonify(dt)

if __name__ == "__main__":
    app.run(
        debug=True,
        host="0.0.0.0",
        port=8080,
    )