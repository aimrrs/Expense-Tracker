from flask import Flask, render_template, request, jsonify, session, redirect
from flask_cors import CORS
from engine import Otp, General, insertRec
from main import RI
from datetime import date, datetime
import calendar

app = Flask(__name__)
app.secret_key = 'zahxom-zIssyx-kedzu2'  # Add a secret key for session
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
        if email in otp_storage:
            return jsonify({"success": True, "message": "Email is send already."})
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
    if not email or not otp:
        return jsonify({"success": False, "message": "Email and OTP are required"}), 400
    
    if email in otp_storage and otp_storage[email] == otp:
        # Check if user is registered
        user = General(email)
        is_registered = user.registered()
        
        if is_registered == False:
            # User is not registered, return success but indicate registration needed
            del otp_storage[email]
            return jsonify({
                "success": True, 
                "registered": False,
                "message": "OTP verified. Please complete registration."
            })
        elif is_registered == True:
            # User is registered, set session and return success
            session['email'] = email
            del otp_storage[email]
            return jsonify({
                "success": True, 
                "registered": True,
                "message": "Login successful"
            })
        else:
            # Error occurred
            return jsonify({"success": False, "message": "Database error"}), 500
    else:
        return jsonify({"success": False, "message": "Invalid OTP"}), 400

@app.route("/register", methods=['GET', 'POST'])
def register():
    if 'email' in session:
        return redirect("/")
    data = request.json
    email = data.get('email')
    name = data.get('name')
    institute = data.get('institute')
    region = data.get('region')
    
    if not email or not name or not institute or not region:
        return jsonify({"success": False, "message": "All fields are required"}), 400
    
    try:
        user = General(email)
        # Create new user
        result = user.newUser(name, institute, region)
        if result == 132:
            return jsonify({"success": False, "message": "Database error"}), 500
        
        # Create database for user
        result = user.createDB()
        if result == 132:
            return jsonify({"success": False, "message": "Database error"}), 500
        
        # Create table for current month
        result = user.createTable()
        if result == 132:
            return jsonify({"success": False, "message": "Database error"}), 500
        
        # Set session
        session['email'] = email
        
        return jsonify({"success": True, "message": "Registration successful"})
    except Exception as err:
        return jsonify({"success": False, "message": str(err)}), 500

@app.route("/login")
def login():
    if 'email' not in session:
        return render_template("login.html")
    else:
        return redirect("/")

@app.route("/")
def index():
    if 'email' not in session:
        return redirect("/login")
    return render_template("main.html")

@app.route("/logout")
def logout():
    session.pop('email', None)
    return redirect("/login")

@app.route("/api/add-expense", methods=['POST'])
def add_expense():
    if 'email' not in session:
        return jsonify({"success": False, "message": "Not authenticated"}), 401
    
    data = request.json
    name = data.get('name')
    amount = data.get('amount')
    category = data.get('category')
    date_str = data.get('date')
    description = data.get('description', 'Null')
    
    if not name or not amount or not category or not date_str:
        return jsonify({"success": False, "message": "Missing required fields"}), 400
    
    try:
        # Initialize user database
        user = General(session['email'])
        db_exists = user.useDB()
        
        if db_exists == 0:
            # Create database if it doesn't exist
            user.createDB()
        
        # Check if table exists for the month
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        month = date_obj.month
        year = date_obj.year
        
        if len(str(month)) == 1:
            table_name = f"m0{month}_{year}"
        else:
            table_name = f"m{month}_{year}"
        
        # Check if table exists, create if not
        if not user.checkTable():
            user.createTable()
        
        # Insert record
        result = insertRec(name, amount, category, None, date_str, description)
        
        if result == 132:
            return jsonify({"success": False, "message": "Database error"}), 500
        
        return jsonify({"success": True, "message": "Expense added successfully"})
    except Exception as err:
        return jsonify({"success": False, "message": str(err)}), 500

@app.route("/api/monthly-data")
def monthly_data():
    if 'email' not in session:
        return jsonify({"success": False, "message": "Not authenticated"}), 401
    
    month = request.args.get('month')
    if not month:
        # Use current month if not specified
        td = date.today()
        M, Y = td.month, td.year
        if len(str(M)) == 1:
            month = f"m0{M}_{Y}"
        else:
            month = f"m{M}_{Y}"
    
    try:
        # Initialize user database
        user = General(session['email'])
        db_exists = user.useDB()
        
        if db_exists == 0:
            # No database, return empty data
            return jsonify({
                "success": True,
                "totalExpense": 0,
                "budget": 1200,  # Default budget
                "categoryBreakdown": {},
                "dailyExpenses": {}
            })
        
        # Check if table exists for the month
        if not user.checkTable():
            # No table for this month, return empty data
            return jsonify({
                "success": True,
                "totalExpense": 0,
                "budget": 1200,  # Default budget
                "categoryBreakdown": {},
                "dailyExpenses": {}
            })
        
        # Get monthly data
        ri = RI()
        month_data = ri.month(month)
        
        # Format data for frontend
        total_expense = month_data.get('totalExpense', 0)
        category_breakdown = {}
        
        # Process category breakdown
        if 'expenseInEachCat' in month_data:
            for cat_data in month_data['expenseInEachCat']:
                category_breakdown[cat_data[0]] = cat_data[1]
        
        # Get daily expenses
        daily_expenses = {}
        month_num = int(month[1:3])
        year = int(month[4:])
        days_in_month = calendar.monthrange(year, month_num)[1]
        
        for day in range(1, days_in_month + 1):
            daily_expenses[day] = 0
        
        # Fill in actual daily expenses
        if 'dailyExpenses' in month_data:
            for day_data in month_data['dailyExpenses']:
                day = day_data[0].day
                amount = day_data[1]
                daily_expenses[day] = amount
        
        return jsonify({
            "success": True,
            "totalExpense": total_expense,
            "budget": 1200,  # Default budget, you can implement budget setting
            "categoryBreakdown": category_breakdown,
            "dailyExpenses": daily_expenses
        })
    except Exception as err:
        return jsonify({"success": False, "message": str(err)}), 500

@app.route("/api/transactions")
def transactions():
    if 'email' not in session:
        return jsonify({"success": False, "message": "Not authenticated"}), 401
    
    month = request.args.get('month')
    if not month:
        # Use current month if not specified
        td = date.today()
        M, Y = td.month, td.year
        if len(str(M)) == 1:
            month = f"m0{M}_{Y}"
        else:
            month = f"m{M}_{Y}"
    
    try:
        # Initialize user database
        user = General(session['email'])
        db_exists = user.useDB()
        
        if db_exists == 0:
            # No database, return empty data
            return jsonify({
                "success": True,
                "transactions": []
            })
        
        # Check if table exists for the month
        if not user.checkTable():
            # No table for this month, return empty data
            return jsonify({
                "success": True,
                "transactions": []
            })
        
        # Get transactions
        # This would need to be implemented in your engine.py or main.py
        # For now, return sample data
        transactions = [
            {
                "id": 1,
                "ename": "Groceries",
                "amount": 45.67,
                "category": "Food & Dining",
                "edate": "2025-03-15",
                "description": "Weekly grocery shopping"
            },
            {
                "id": 2,
                "ename": "Bus Fare",
                "amount": 12.50,
                "category": "Transport",
                "edate": "2025-03-16",
                "description": "Weekly bus pass"
            }
        ]
        
        return jsonify({
            "success": True,
            "transactions": transactions
        })
    except Exception as err:
        return jsonify({"success": False, "message": str(err)}), 500

@app.route("/api/set-budget", methods=['POST'])
def set_budget():
    if 'email' not in session:
        return jsonify({"success": False, "message": "Not authenticated"}), 401
    
    data = request.json
    amount = data.get('amount')
    month = data.get('month')
    year = data.get('year')
    
    if not amount or not month or not year:
        return jsonify({"success": False, "message": "Missing required fields"}), 400
    
    try:
        # This would need to be implemented in your database structure
        # For now, just return success
        return jsonify({
            "success": True,
            "message": "Budget set successfully"
        })
    except Exception as err:
        return jsonify({"success": False, "message": str(err)}), 500

@app.route("/api/delete-expense", methods=['DELETE'])
def delete_expense():
    if 'email' not in session:
        return jsonify({"success": False, "message": "Not authenticated"}), 401
    
    expense_id = request.args.get('id')
    if not expense_id:
        return jsonify({"success": False, "message": "Expense ID is required"}), 400
    
    try:
        # This would need to be implemented in your database structure
        # For now, just return success
        return jsonify({
            "success": True,
            "message": "Expense deleted successfully"
        })
    except Exception as err:
        return jsonify({"success": False, "message": str(err)}), 500

if __name__ == "__main__":
    app.run(debug=True,
            host='0.0.0.0',
            port='8080')