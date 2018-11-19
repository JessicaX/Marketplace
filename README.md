###How to Start
1. Make sure you are using python 3.6+
2. Clone the project into your local repo
3. Run `python -m venv ENV` to create virtual environment
4. Switch to virtual environment
    For windows, in cmd console run `ENV\Scripts\activate`
    For Linux, in terminal run `source ENV/bin/activate`
    You should be able to see the console switch to `ENV`
5. Run `pip install -r requirements.txt`. This step is to install the dependent modules
6. Start the application
    For windows `.\start.ps1`
    For Linux `Haven't tried`
    For Max `export FLASK_APP=hello.py`
            `flask run`

###To Do List
* ~~Index page~~
* ~~Register~~
* ~~Login~~
* Add sell item `in progress`
* Image upload `in progress`
* Single item page `in progress`
* Personal page shows all the item the person uploaded `in progress`
* wishinglist shows all the items the customers liked
* Related items
* Categories
* .......

###How to test the html template
* go to main.py
*
* type the code and replace parameter accordingly:
*
* @app.route("/name_of_the_page")
*   def name_of_the_page():
*       return render_template("name_of_the_page.html")
*
* save and type in the browser "http://http://127.0.0.1:5000/name_of_the_page" 


