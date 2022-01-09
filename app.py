# Store this in 'app.py' file

from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import pywhatkit as kit
import bs4
import requests

app = Flask(__name__)

app.secret_key = 'secret_key'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'userprofile'

mysql = MySQL(app)


# @app.route('/login', methods=["GET", "POST"])
# def login():
#     msg = ""
#     if request.method == "POST" and "username" in request.form and 'password' in request.form:
#         username = request.form['username']
#         password = request.form['password']
#         cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
#         cursor.execute('SELECT * FROM accounts WHERE username = % s AND password = % s', (username, password))
#         account = cursor.fetchone()
#         if account:
#             session['loggedin'] = True
#             session['id'] = account['id']
#             session['username'] = account['username']
#             msg = 'Logged in successfully!'
#             return render_template('index.html', msg=msg)
#         else:
#             msg = 'Incorrect username / password'
#     return render_template('login.html', msg=msg)

@app.route("/search", methods = ["POST", "GET"])
def redirecting():
	if request.method == "POST":
		city1 = request.form["nm"]
		return redirect(url_for("hospital_search", city = city1))
	else:
		return render_template("index.html")

@app.route("/<city>")
def hospital_search(city):
	search = f"Hospitals near {city}"
	url = 'https://google.com/search?q=' + search

	# Fetch the URL data using requests.get(url),
	# store it in a variable, request_result.
	request_result=requests.get( url )

	# Creating soup from the fetched request
	soup = bs4.BeautifulSoup(request_result.text, "html.parser")

	heading_object = soup.find_all('h3')
	counter = 0
	the_info = []
	address_list = []

	for info in heading_object:
		the_info.append(info.getText())
		counter += 1
		if counter == 3:
			return f"<h2>The Hospitals Near {city} are: </h2>" +  f"1. {the_info[0]}" + "<br>" + "<br>" + f"2. {the_info[1]}" + "<br>" \
                   + "<br>" + f"3. {the_info[2]}</h3>"

@app.route("/address", methods = ["POST", "GET"])
def address():
	if request.method == "POST":
		name = request.form["name"]
		kit.search(str(name) + " address")
		return f"<h1>We have searched {name} in new tab!</h1>"
	else:
		return render_template("address.html")

@app.route('/information')
def information():
    return render_template("information.html")

@app.route('/covid_info')
def covid_info():
    return render_template("covid_info.html")

@app.route('/result', methods=["GET", "POST"])
def result():
    disease = []
    # f = open("dis_symp_dict.txt", encoding="utf8")
    # lines = f.read().split('\n')
    # print(lines, flush=True)
    with open("dis_symp_dict.txt", encoding="utf8") as file:
        disease = file.readlines()
        disease = [line.rstrip().strip('][').split(', ') for line in disease]
    print(disease, flush=True)

    symptom_possible = []
    query = request.form["searchbar"]
    queryarr = query.split(", ")
    print(query, flush=True)
    for i in range(len(disease)):
        for j in range(len(disease[i])):
            for l in range(len(queryarr)):
                print(disease[i][j].replace('"', '') == queryarr[l], flush=True)
                if disease[i][j].replace('"', '').replace("'", '') == queryarr[l]:
                    symptom_possible.append(disease[i])
                if len(symptom_possible) == 15:
                    break
            if len(symptom_possible) == 15:
                break
        if len(symptom_possible) == 15:
            break
    final_results = []
    for arr in symptom_possible:
        inner_res = []
        inner_res.append(arr[0])
        str_data = ", ".join(arr[1:])
        inner_res.append(str_data)
        final_results.append(inner_res)
    # print(final_results, flush=True)

    return render_template("symptom.html", results=final_results)

@app.route('/')
@app.route('/symptom')
def symptom():

    return render_template("symptom.html")

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    msg=''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form and 'address' in request.form and 'city' in request.form and 'country' in request.form and 'postalcode' in request.form and 'organization' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        organization = request.form['organization']
        address = request.form['address']
        city = request.form['city']
        state = request.form['state']
        country = request.form['country']
        postalcode = request.form['postalcode']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = % s', (username,))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'name must contain only characters and numbers !'
        else:
            cursor.execute('INSERT INTO accounts VALUES (NULL, % s, % s, % s, % s, % s, % s, % s, % s, % s)',
                           (username, password, email, organization, address, city, state, country, postalcode,))
            mysql.connection.commit()
            msg = 'You have successfully registered !'
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('register.html', msg=msg)

# @app.route('/index')
# def index():
#     if 'loggedin' in session:
#         return render_template("index.html")
#     return redirect(url_for('login'))

@app.route("/display")
def display():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE id = % s', (session['id'], ))
        account = cursor.fetchone()
        return render_template("display.html", account = account)
    return redirect(url_for('login'))

@app.route("/update", methods=['GET', 'POST'])
def update():
    msg = ''
    if 'loggedin' in session:
        if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form and 'address' in request.form and 'city' in request.form and 'country' in request.form and 'postalcode' in request.form and 'organization' in request.form:
            username = request.form['username']
            password = request.form['password']
            email = request.form['email']
            organization = request.form['organization']
            address = request.form['address']
            city = request.form['city']
            state = request.form['state']
            country = request.form['country']
            postalcode = request.form['postalcode']
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM accounts WHERE username = % s', (username,))
            account = cursor.fetchone()
            if account:
                msg = 'Account already exists !'
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                msg = 'Invalid email address !'
            elif not re.match(r'[A-Za-z0-9]+', username):
                msg = 'name must contain only characters and numbers !'
            else:
                cursor.execute(
                    'UPDATE accounts SET  username =% s, password =% s, email =% s, organization =% s, address =% s, city =% s, state =% s, country =% s, postalcode =% s WHERE id =% s',
                    (username, password, email, organization, address, city, state, country, postalcode,
                     (session['id'],),))
                mysql.connection.commit()
                msg = 'You have successfully updated !'
        elif request.method == 'POST':
            msg = 'Please fill out the form !'
        return render_template("update.html", msg=msg)
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(host="localhost", port=int("5000"))
