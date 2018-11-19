from flask import Flask, render_template, request, redirect, jsonify, session
from sql_client import MySqlClient
import utils
import cloudinary
import cloudinary.uploader

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

client = MySqlClient()

@app.route("/")
def index():
    items = client.get_latest_items()
    return render_template('index.html', items=items)

@app.route("/checkusername/<username>")
def check_username_usability(username):
    rowcount = client.check_username(username)
    return jsonify({"status": rowcount == 0})

@app.route("/register", methods=["POST"])
def register():
    data = request.form
    username = data["username"]
    password = data["password"]
    cpassword = data["cpassword"] 
    #TODO: here should check username and password valid or not in backend
    #Lazy to change if got time, should do
    client.register(username, utils.md5_hash(password))
    session["user"] = client.get_user_by_name(username)
    return redirect("/")

@app.route("/login", methods=["POST"])
def login():
    data = request.form
    username = data["username"].strip()
    password = data["password"]
    user = client.get_user_by_username_password(username, utils.md5_hash(password))
    if user is not None:
        session["user"] = user
    else:
        flash(u'Login failed. Wrong username or password.', 'danger')
    return redirect("/")

@app.route("/logout")
def logout():
    del session["user"]
    return redirect("/")

@app.route("/sell")
def sell():
    return render_template("sell.html")

@app.route("/singlepage")
def signlepage():
    return render_template("singlepage.html")

@app.route("/uploadimage", methods=["POST"])
def upload():
    cloudinary.config(
        cloud_name='yybird', 
        api_key= 'xx', # please check with me the api_key 
        api_secret= 'xx' # please check with me the parameter
    )
    files = request.files.getlist("files[]")
    for file in files:
        print(cloudinary.uploader.upload(file))
    return redirect("/sell")