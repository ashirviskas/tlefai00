from flask import Flask
from flask import render_template




app = Flask(__name__)

@app.route('/')
def mains():
    return render_template('layout.html')

@app.route('/login/')
def login():
    return render_template('login.html')

