from flask import Flask, render_template, request, json, redirect, session
from flask import Markup
import requests

app = Flask(__name__)
app.config["DEBUG"] = False

@app.route("/")
def home():
    return render_template('home.html')

@app.route("/result")
def result():
    headers = {
        'Authorization': 'Bearer <your API key>',
    }

    params = (
        ('maxRecords', '25'),
        ('view', 'Main View'),
    )

    r = requests.get('https://api.airtable.com/v0/<your app id>/Tasks?api_key=<your API key>&sortField=_createdTime&sortDirection=desc', headers=headers, params=params)
    dict = r.json()
    dataset = []
    name_list = []
    time_estimate_list = []
    status_list = []
    for i in dict['records']:
         dict = i['fields']
         del dict["Design_Projects"]
         del dict["Assignee"]
         del dict["Stage"]
         dataset.append(dict)
    for dicts in dataset:
        name_list.append(dicts.get('Name'))
        time_estimate_list.append(dicts.get('Time_Estimate'))
        status_list.append(dicts.get('Completed'))
    return render_template('result.html', tasks = name_list, estimates = time_estimate_list, statuses = status_list)

@app.route("/table")
def table():
    headers = {
        'Authorization': 'Bearer <your API key>',
    }

    params = (
        ('maxRecords', '25'),
        ('view', 'Main View'),
    )

    r = requests.get('https://api.airtable.com/v0/<your App ID>/Tasks?api_key=<your API key>&sortField=_createdTime&sortDirection=desc', headers=headers, params=params)
    dict = r.json()
    dataset = []
    for i in dict['records']:
         dict = i['fields']
         del dict["Design_Projects"]
         del dict["Assignee"]
         del dict["Stage"]
         dataset.append(dict)
    return render_template('table.html', entries=dataset)


@app.route("/login")
def login():
    return render_template('login.html')

@app.route("/process",methods=['POST'])
def process():
    email = request.form['email']
    password = request.form['password']
    message = "Email is: " + email + " and the password is: " + password
    return render_template('home.html', message=message)

if __name__ == '__main__':
   app.run(debug = True)
