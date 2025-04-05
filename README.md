# StudentSpend – Expense Tracker

**StudentSpend** is a web-based expense tracking application designed to help students efficiently manage their expenses.

---

## 🚀 Features

- **User Authentication**: Secure login using OTP-based authentication.
- **Expense Tracking**: Add, edit, and delete expenses with details like name, amount, category, date, and description.
- **Dashboard**: View total expenses, transaction count, and the category with the highest spending.
- **Monthly Analytics**: Track expenses month by month and view detailed transaction history.
- **Responsive Design**: Optimized for both desktop and mobile devices.

---

## 🗂️ Project Structure

```
Expense-Tracker/
│
├── app.py                  # Main Flask application
├── engine/                 # Core logic for database operations
│   └── test.py             # Test script for verifying functionality
├── templates/              # HTML templates for the web interface
│   ├── login.html          # Login page
│   ├── main.html           # Dashboard page
├── static/                 # Static assets (CSS, JS)
│   ├── styles/             # Stylesheet for the application
│       └── style.css
│   ├── js/
│       └── login.js        # JavaScript for client-side functionality
├── logs/
│   └── err.log             # Error log
├── worklog/                # Work log (if applicable)
├── pycache/                # Compiled Python files
├── README.md               # Project documentation
└── requirements.txt        # Python dependencies
```

---

## ⚙️ Installation

1. **Clone the repository**:

```bash
git clone https://github.com/your-username/Expense-Tracker.git
cd Expense-Tracker
```

2. **Install dependencies**:

```bash
pip install -r requirements.txt
```

3. **Configure the database**:
   - Update the `DB_CONN` in `config.py` with your MySQL database credentials.
   - Ensure the required tables (`user_spend`, `user_information`, etc.) are created in the database.

4. **Configure email settings**:
   - Update `MAIL_USERNAME` and `MAIL_PASSWORD` in `config.py` with your email credentials.

5. **Run the application**:

```bash
python app.py
```

6. **Access the application** at [http://localhost:8080](http://localhost:8080)

---

## 📡 API Endpoints

### Authentication
- `POST /send-otp` - Generate and send an OTP to the user’s email.
- `POST /verify-otp` - Verify the OTP for login.
- `POST /register` - Register a new user.

### Expense Management
- `GET /api/get-transactions` - Fetch transactions for the authenticated user.
- `POST /api/add-expense` - Add a new expense.
- `DELETE /api/delete-expense` - Delete an expense.

### User Information
- `GET /api/user-info` - Fetch user details.
- `GET /api/get-card-data` - Fetch dashboard card data for a specific month and year.

---

## 🛠️ Technologies Used

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, JavaScript
- **Database**: MySQL
- **Email Service**: Flask-Mail
- **Logging**: Custom error logging to `logs/err.log`

---

## 🔮 Future Enhancements

- Add analytics for yearly expense trends.
- Implement user-defined categories for better customization.
- Add support for exporting data to CSV or PDF.
- Enhance security with additional authentication mechanisms.

---

## 📝 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## 🙌 Acknowledgments

- [Font Awesome](https://fontawesome.com) for icons.
- [Google Fonts](https://fonts.google.com) for the Inter font.
