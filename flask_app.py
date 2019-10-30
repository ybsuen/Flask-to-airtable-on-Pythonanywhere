from flask import Flask, render_template, json, request, redirect, session
from flask import Markup
from flaskext.mysql import MySQL
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin
import requests
import bcrypt

mysql = MySQL()
app = Flask(__name__)
app.config['SESSION_TYPE'] = 'memcached'
app.secret_key = 'why would I tell you my secret key?'
app.config['TEMPLATES_AUTO_RELOAD'] = True

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'xxxxxxxxxxx'
app.config['MYSQL_DATABASE_PASSWORD'] = 'xxxxxxxxxxx'
app.config['MYSQL_DATABASE_DB'] = 'xxxxxxxxxxx'
app.config['MYSQL_DATABASE_HOST'] = 'xxxxxxxxxxx'
mysql.init_app(app)

app.config["DEBUG"] = False
app.config['SECRET_KEY'] = "xxxxxxxxxxx"
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

class User(UserMixin):
  def __init__(self,id):
    self.id = id

@app.route("/")
@login_required
def home():
    return render_template('home.html')

@app.route("/list_users")
@login_required
def table():
    headers = {
        'Authorization': 'Bearer <replace with your own Airtable API key>',
    }

    r = requests.get('https://api.airtable.com/v0/<replace with your own Airtable App key>/Users?sortField=_createdTime&sortDirection=desc', headers=headers)
    dict = r.json()
    dataset = []
    for i in dict['records']:
         dict = i['fields']
         dataset.append(dict)
    return render_template('table.html', entries=dataset)

@app.route("/chart")
@login_required
def chart():
    headers = {
        'Authorization': 'Bearer <replace with your own Airtable API key>',
    }

    params = (
        ('view', 'Grid view'),
    )

    r = requests.get('https://api.airtable.com/v0/<replace with your own Airtable App key>/Roll-up?api_key=<replace with your own Airtable API key>', headers=headers, params=params)
    dict1 = r.json()
    dict2 = {}
    dataset = []
    name_list = []
    total_entries_list = []
    for i in dict1['records']:
         dict2 = i['fields']
         dataset.append(dict2)
    for item in dataset:
        name_list.append(item.get('Name'))
        total_entries_list.append(item.get('total_items_by_category'))
    return render_template('flask_chart.html', entries = zip(name_list, total_entries_list))

@app.route("/map")
@login_required
def map():
    headers = {
        'Authorization': 'Bearer <replace with your own Airtable API key>',
    }

    params = (
        ('view', 'Grid view'),
    )
    r = requests.get('https://api.airtable.com/v0/<replace with your own Airtable App key>/Venues?api_key=<replace with your own Airtable API key>', headers=headers, params=params)
    dict = r.json()
    dataset = []
    data = []
    items = {}
    total_entries_list = []
    for i in dict['records']:
         dict = i['fields']
         dataset.append(dict)
    return render_template('map.html', entries = dataset)

@app.route("/login")
def login():
    message = 'Please login in first.'
    return render_template('login.html', message=message)

@app.route("/user")
@login_required
def user():
    message = 'Please enter user information.'
    return render_template('userform.html', message=message)

@app.route("/adduser",methods=['POST'])
@login_required
def adduser():
    fname = request.form['fname']
    lname = request.form['lname']
    student_id = request.form['student_id']
    date_of_birth = request.form['date_of_birth']
    pwd = request.form['pwd']
    pwd = pwd.encode('UTF-8')
    # Hash a password for the first time, with a randomly-generated salt
    hashed = bcrypt.hashpw(pwd, bcrypt.gensalt())
    pwd = hashed.decode('UTF-8')
    mydict =  {
        "fname": fname,
        "lname": lname,
        "student_id": student_id,
        "date_of_birth": date_of_birth,
        'pwd': pwd
    }
    data = {"fields": mydict}
    headers = {'Authorization': 'Bearer <replace with your own Airtable API key>', 'Content-Type': 'application/json; charset=utf-8'}
    r = requests.post('https://api.airtable.com/v0/<replace with your own Airtable App key>/Users',json=data,headers=headers)
    message = 'Please enter user information.'
    return render_template('home.html',message=message)

@app.route("/updateuser",methods=['POST','PUT'])
@login_required
def updateuser():
    record_id = request.form['record_id']
    headers = {
        'Authorization': 'Bearer <replace with your own Airtable API key>',
    }
    r = requests.get('https://api.airtable.com/v0/<replace with your own Airtable App key>/Users/' + record_id, headers=headers)
    dict = r.json()
    dict_list = dict['fields']
    for i in dict_list:
        if (i == 'pwd'):
            pwd = dict_list[i]

    fname = request.form['fname']
    lname = request.form['lname']
    student_id = request.form['student_id']
    date_of_birth = request.form['date_of_birth']

    fields =  {
    "fname": fname,
    "lname": lname,
    "student_id": student_id,
    "date_of_birth": date_of_birth,
    "pwd": pwd
    }

    data = {
      "records": [
          {
          "id": record_id,
          "fields": fields
          }
      ]
    }

    headers = {'Authorization': 'Bearer <replace with your own Airtable API key>', 'Content-Type': 'application/json; charset=utf-8'}
    r = requests.put('https://api.airtable.com/v0/<replace with your own Airtable App key>/Users',json=data,headers=headers)
    message = 'Please enter user information.'
    return render_template('home.html',message=message)

@app.route("/deleteuser",methods=['POST','DELETE'])
@login_required
def deleteuser():
    url = "https://api.airtable.com/v0/<replace with your own Airtable App key>/Users/"
    record_id = request.form['record_id']
    headers = {'Authorization': 'Bearer <replace with your own Airtable API key>', 'Content-Type': 'application/x-www-form-urlencoded'}
    # r = requests.delete('https://api.airtable.com/v0/appM38HXlEVhxmnqx/flaskdemo/reczHAuDe1UxDw5HW',headers=headers)
    r = requests.delete(url + record_id, headers=headers)
    message = 'Please enter user information.'
    return render_template('home.html',message=message)

@app.route("/process",methods=['POST'])
def process():
    student_id = request.form['student_id']
    password = request.form['password']
    password = password.encode('UTF-8')
    hashed = ''
    user = ''
    headers = {
    'Authorization': 'Bearer <replace with your own Airtable API key>',
    }

    # filter = 'IF(AND({UserName}="'+username+'",{Pwd}="'+password+'"), 1, 0)'
    filter = 'IF(({student_id}="'+student_id+'"), 1, 0)'

    params = (
        ('view', 'Grid view'),
        ('filterByFormula', filter),
    )

    dataset = []
    r = requests.session()
    r = requests.get('https://api.airtable.com/v0/<replace with your own Airtable App key>/Users?sortField=_createdTime&sortDirection=desc', headers=headers, params=params)

    dict = r.json()

    for i in dict['records']:
         dict = i['fields']
         dataset.append(dict)
    for item in dataset:
        user = item.get('student_id')
        if user != None:
            hashed = item.get('pwd')
            fname = item.get('fname')
            hashed = hashed.encode('UTF-8')
        else:
            message = 'wrong password!'
            return render_template('login.html',message=message)

    if  student_id == user and bcrypt.checkpw(password, hashed):
        login_user(User(1))
        user = {"name":"Flask-Airtable REST API Demo"}
        message = "Dear " + fname + ", welcome to this Flask Airtable REST API demo app. Your login has been granted."
        return render_template('home.html', user=user, title="home page",message=message)
    message = 'wrong password!'
    return render_template('login.html',message=message)

@app.errorhandler(500)
def internal_error(error):
    message = 'wrong password!'
    return render_template('login.html',message=message),500

@app.route('/logout/')
@login_required
def logout():
    logout_user()
    message = 'Thanks for logging out.'
    return render_template('login.html',message=message)

if __name__ == '__main__':
   app.run(debug = True)
