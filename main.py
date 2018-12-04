from flask import Flask, render_template, request, redirect, jsonify, session, flash
from sql_client import MySqlClient
import utils
import cloudinary
import cloudinary.uploader

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

client = MySqlClient()
@app.template_filter('resize')
def resize_filter(s, size):
    return s.replace("image/upload", "image/upload/"+size)

@app.route("/")
def index():
    items = client.get_latest_items()
    categories = client.get_all_categories()
    return render_template('index.html', items=items, categories=categories)

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
    # join_date = client.get_user_by_join_date(username)
    if user is not None:
        session["user"] = user
        # session["join_date"] = join_date
    else:
        flash(u'Login failed. Wrong username or password.', 'danger')
    return redirect("/")

@app.route("/logout")
def logout():
    del session["user"]
    return redirect("/")

@app.route("/sell")
def sell():
    categories = client.get_all_categories()
    return render_template("sell.html", categories=categories)

@app.route("/createitem", methods=["POST"])
def create_item():
    data = request.form
    user = session["user"]
    item = client.create_item(user["Id"], data)
    categories = data.getlist('Category')
    print(categories)
    if len(categories) > 0:
        client.add_categories_to_item(item[0]["Id"], categories)
    return redirect("/edititem/%s"%item[0]["Id"])

@app.route("/edititem/<item_id>")
def edit_item(item_id):
    print(request.referrer)
    item = client.get_item_by_id(item_id)[0]
    categories = [d["categoryid"] for d in client.get_item_categories(item_id)]
    images = client.get_images_by_item_id(item_id)
    allcategories = client.get_all_categories()
    return render_template("edit.html", item=item, images=images, categories=categories, allcategories=allcategories)

@app.route("/updateitem", methods=["POST"])
def update_item():
    try:
        data = request.form
        id = data["Id"]
        categories = data.getlist("Category")
        client.update_item(data)
        o_categories = [str(c["categoryid"]) for c in client.get_item_categories(id)]
        print(o_categories)
        i_categories = []
        d_categories = []
        for c in categories:
            if c not in o_categories:
                i_categories.append(c)

        for o in o_categories:
            if o not in categories:
                d_categories.append(o)

        print(i_categories)
        print(d_categories)

        if len(i_categories) > 0:
            client.add_categories_to_item(id, i_categories)

        if len(d_categories) > 0:
            client.delete_categories(id, d_categories)

        flash(u'Update successfully.', 'success')
        return redirect("/edititem/"+id)
    except Exception as ex:
        print(str(ex))
        flash(u'Update failed!', 'danger')

@app.route("/singlepage/<id>")
def signlepage(id):
    item = client.get_item_by_id(id)[0]
    images = client.get_images_by_item_id(id)
    likes = client.get_item_likes(session['user']['Id'], id)
    return render_template("singlepage.html", item=item, images=images, likes=likes[0])

@app.route("/profilepage")
def profilepage():
    items = client.get_latest_items()
    return render_template('profilepage.html', items=items)

@app.route("/wishing")
def wishing():
    items = client.get_latest_items()
    return render_template('wishing.html', items=items)

@app.route("/category/<category_id>")
def category(category_id):
    items = client.get_item_by_category_id(category_id)
    # items = client.get_item_by_category_id(session["category"]["Id"])
    return render_template('category.html', items=items)

@app.route("/uploadimage/<itemid>", methods=["POST"])
def upload(itemid):
    cloudinary.config(
        cloud_name='yybird', 
        api_key= 'xxx',
        api_secret= 'xxx'
    )
    files = request.files.getlist("files[]")
    for file in files:
        resp = cloudinary.uploader.upload(file)
        print(resp)
        client.add_image_to_item(itemid, resp["url"])
    return redirect("/edititem/%s"%itemid)

@app.route("/deleteimage/<item_id>", methods=["POST"])
def deleteimg(item_id):
    data = request.form#{"imageid": 1}
    id = data["imageid"]
    client.delete_image_by_imageid(id)
    flash(u'Delete successfully.', 'success')
    return redirect("/edititem/"+item_id)

@app.route("/like/<item_id>", methods=["POST"])
def like_item(item_id):
    client.like_item(session['user']["Id"], item_id)
    return redirect("/singlepage/%s"%item_id)

@app.route("/comment/<item_id>", methods=["POST"])
def make_comment(item_id):
    message = request.form["message"]
    client.make_comment(session['user']['Id'], item_id, message)
    return redirect("/singlepage/%s"%item_id)

@app.route("/myitems")
def my_items():
    items = client.get_my_items(session["user"]["Id"])
    return render_template("myitem.html", items=items)

@app.route("/profile")
def profile():
    return render_template("profile.html")

@app.route("/myfavourites")
def my_favourites():
    items = client.get_my_favourites(session["user"]["Id"])
    return render_template("myfavourites.html", items=items)

@app.route("/searchpage")
def searchpage():
    searchitem = request.args.get("searchitem")
    items = client.get_search_items_by_name(searchitem)
    # categories = client.get_all_categories()
    return render_template('searchpage.html', items=items, searchitem=searchitem)