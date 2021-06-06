from flask import Flask, render_template, url_for, request
from werkzeug.security import generate_password_hash, check_password_hash
import pymongo, random

app = Flask(__name__)
def generateuid(fname, lname):
    #9 long string
    uid = str(ord(fname[0])) + str(ord(lname[0]))
    while len(uid) < 9:
        uid += str(random.randint(0,9))  
    return uid

with open("password.txt", 'r') as file:
    client = pymongo.MongoClient(file.read())
    db = client["LoginDB"]
    coll = db["LoginColl"]

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods = ["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html", action = "Log In", title = "Login")
    else:
        uid = request.form['uid']
        pin = request.form['pin']
        query = {'uid': uid}
        found = coll.find(query)
        account = dict()
        for item in found:
            account = item  
        if check_password_hash(account['pin'], pin):
            return render_template('result.html', result = f"Hey {account['fname']}", funds = account['money'])
        
        return render_template('result.html', result = "Login Unsuccessful!")

@app.route("/register", methods = ["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html", action = "Sign Up", title = "Register")
    else:
        fname = request.form['fname']
        lname = request.form['lname']
        pin = request.form['pin']

        if len(fname) >= 2 and len(lname) >= 2 and len(pin) == 4:

            uniqueid = generateuid(fname, lname)    
            hashedpin = generate_password_hash(pin)
            coll.insert_one({'fname': fname, "lname": lname, 'uid': uniqueid, "pin": hashedpin, 'money': 0})
            return render_template('result.html', uid = uniqueid, result = "Registration Successful!")
        else:
            return render_template('result.html', result = "Registration Unsuccessful! Please check data and try again!")
@app.route("/addfunds", methods = ["GET", "POST"])
def addfunds():
    if request.method == "GET":
        return render_template("addfunds.html", action = "Add Funds", title = "Add Funds")
    else:
        uid = request.form['uid']
        pin = request.form['pin']
        newfunds = request.form["funds"]

        query = {'uid': uid}
        found = coll.find(query)
        account = dict()
        for item in found:
            account = item
        if check_password_hash(account['pin'], pin):
            coll.update_one({
            '_id' : account['_id']
            },{
                '$set': {
                    'money': account['money'] + int(newfunds)
                }
            }, upsert=False)
            return render_template('result.html', result = "Action Successful")
        else:
            return render_template('result.html', result = "Incorrect Password! Please check data and try again!")

       

@app.route("/transferfunds", methods = ["GET", "POST"])
def transferfunds():
    if request.method == "GET":
        return render_template("transferfunds.html", action = "Transfer Funds", title = "Transfer Funds")
    else:
        sourceuid = request.form['sourceuid']
        pin = request.form['pin']
        funds = request.form["funds"]
        destuid = request.form['destuid']

        query = {'uid': sourceuid}
        found = coll.find(query)
        saccount = dict()
        for item in found:
            saccount = item
        if check_password_hash(saccount['pin'], pin):
            query = {'uid': destuid}
            found = coll.find(query)
            daccount = dict()
            for item in found:
                daccount = item
            coll.update_one({
            '_id' : saccount['_id']
            },{
                '$set': {
                    'money': saccount['money'] - int(funds)
                }
            }, upsert=False)

            coll.update_one({
            '_id' : daccount['_id']
            },{
                '$set': {
                    'money': daccount['money'] + int(funds)
                }
            }, upsert=False)

            return render_template('result.html', result = "Action Successful")
        else:
            return render_template('result.html', result = "Incorrect Data! Please try again!")


@app.route("/recover", methods = ["GET", "POST"])
def recover():

    if request.method == "GET":
        return render_template('recover.html')
    else:
        fname = request.form['fname']
        lname = request.form['lname']
        pin = request.form['pin']

        query = {'fname': fname, 'lname': lname}
        found = coll.find(query)
        print(query)
        account = dict()
        for item in found:
            account = item
        print(account)
        try:
            if check_password_hash(account['pin'], pin):
                return render_template('result.html', result = f"Your UID is {account['uid']}")
            else:
                return render_template('result.html', result = "Incorrect Data! Please try again!")
        except:
            return render_template('result.html', result = "Incorrect Data! Please try again!")

if __name__ == "__main__":
    app.run(debug=True)