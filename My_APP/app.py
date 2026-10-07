

from flask import Flask, render_template, request, redirect, session
from flask_mail import Mail, Message
from dotenv import load_dotenv
import os
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import random

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "users.db")

app = Flask(__name__)

load_dotenv()

app.secret_key = os.getenv("SECRET_KEY")

app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USE_TLS"] = False
app.config["MAIL_USE_SSL"] = True
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")
mail = Mail(app)


#Create a database 
def create_database():
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, email TEXT UNIQUE NOT NULL, password TEXT NOT NULL, verification_code TEXT, verified INTEGER DEFAULT 0)
    """)

    connection.commit()
    connection.close()

# Home page
@app.route("/")
def home():
    return "Welcome to my website! Please <a href='/register'>Register</a> or <a href='/login'>Login</a> to continue."



# Register page
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]


        # Check passwords 
        if password != confirm_password:
            return "Passwords do not match."

        # Generate  a 6-digitverification code
        verification_code = random.randint(100000, 999999)

        # Hash the password
        hashed_password = generate_password_hash(password)

        # Connect to database
        connection = sqlite3.connect(DATABASE)
        cursor = connection.cursor()

        try:
            cursor.execute(
                "INSERT INTO users (name, email, password, verification_code, verified) VALUES (?, ?, ?, ?, ?)", (name, email, hashed_password, str(verification_code), 0)
            )
            
            connection.commit()

            # Send verification email
            msg = Message(
                "Verify your account",
                sender=app.config["MAIL_USERNAME"],
                recipients=[email]
            )
            
            msg.body = f"""Hello {name}, Your verification code is: {verification_code} Enter this code on the verification page to verify your account. Thank you!
            """
            mail.send(msg)


            return redirect("/verify")
        
        except sqlite3.IntegrityError:
            return "Error: Email already exists."
        finally:
            connection.close()

    return render_template("register.html")

# Verify email page
@app.route("/verify", methods=["GET", "POST"])
def verify():
    if request.method == "POST":
        email = request.form["email"]
        entered_code = request.form["verification_code"]

        connection = sqlite3.connect(DATABASE)
        cursor = connection.cursor()

        cursor.execute("SELECT verification_code, verified FROM users WHERE email = ?", (email,)
        )
        user = cursor.fetchone()
        if user is None:
            connection.close()
            return "No account found with that email."
        if user[1] == 1:
            connection.close()
            return "This acoount is already verified."
        if user[0] == entered_code:
            cursor.execute("""UPDATE users SET verified = 1, verification_code = NULL WHERE email = ?""", (email,)
            )

            connection.commit()
            connection.close()

            return redirect("/login")

        connection.close()
        return "Incorrect verification code. Try again."

    return render_template("verify.html")


# Login page
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        connection = sqlite3.connect(DATABASE)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,)
        )
        user = cursor.fetchone()

        if user is None:
            connection.close()
            return "Email or password is incorrect."
        
        # Check password
        if not check_password_hash(user[3], password):
            connection.close()
            return "Email or password is incorrect."
        
        # Check email verification
        if user[5] == 0:

            # Generate a new 6-digit code
            verification_code = random.randint(100000, 999999)

            # Save the new code
            cursor.execute("UPDATE users SET verification_code = ? WHERE email =?", (str(verification_code), email)
            )

            connection.commit()
            connection.close()

            # Send new Verification email
            msg = Message(
                "Your new verification code", sender=app.config["MAIL_USERNAME"],
                recipients=[email]
            )
            
            msg.body = f"""Hello {user[1]}, Your new verification code is: {verification_code} Enter this code on the verification page to verify your account. Thank you!
            """
            mail.send(msg)

            return redirect("/verify")
        connection.close()
        
        session["user_id"] = user[0]
        session["user_name"] = user[1]

        return redirect("/dashboard")
    
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")
    
    return render_template("dashboard.html", name=session["user_name"])

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

create_database()

# Start server 
if __name__ == "__main__":
    app.run(debug=True)
