from flask import Flask, render_template, url_for, request
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector

app = Flask(__name__)

with open("password.txt", "r") as passwd:
    # connects to the db server
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password=passwd.read(),
        database="loginsystem"
    )

cursor = db.cursor(buffered=True)




@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods = ["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html", action = "Log In", title = "Login")
    else:
        username = request.form['username']
        password = request.form['password']
        cursor.execute("SELECT * FROM Credentials WHERE username = %s", (username,))
        row = cursor.fetchone()
        hashedpass = row[1]

        if check_password_hash(hashedpass, password):
            return render_template('result.html', result = "Login Successful!")
        else:
            return render_template('result.html', result = "Login Unsuccessful!")


@app.route("/register", methods = ["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html", action = "Sign Up", title = "Register")
    else:
        username = request.form['username']
        password = request.form['password']
        # checks if the username is used
        pswrd = generate_password_hash(password)
        cursor.execute("SELECT EXISTS(SELECT * FROM Credentials WHERE username = %s)", (username,))
        usernamefetch = cursor.fetchone()
        usernameexists = usernamefetch[0]
        cursor.execute("SELECT EXISTS(SELECT * FROM Credentials WHERE password = %s)", (password,))
        passwordfetch = cursor.fetchone()
        passwordexists = passwordfetch[0]

        if usernameexists:
            if passwordexists:
                # both are correct
                return render_template('result.html', result = "This combination is already used. You need to log in!")
            else:
                # just the username is correct, not the password
                return render_template('result.html', result = "This username is not available! Please choose another one and try again!")

        else:
            # new acc, needs to be registered
            cursor.execute("INSERT INTO Credentials (username, password) VALUES (%s, %s)", (username, pswrd))
            db.commit()
            return render_template('result.html', result = "Registration Successful!")



if __name__ == "__main__":
    app.run(debug=True)