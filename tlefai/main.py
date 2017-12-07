
from flask import Flask, url_for
from flask import render_template
from flask import request
import importlib

from tlefai import kliento_autorizacijos_valdiklis



app = Flask(__name__)

@app.route('/')
def mains():
    return render_template('index.html')

@app.route('/login/', methods=['POST', 'GET'])
def login():
    error = None
    if request.method == 'POST':
        if kliento_autorizacijos_valdiklis.patikrinti_duomenis(request.form['email'],
                       request.form['password']):
            print("Logged in success")
            return kliento_autorizacijos_valdiklis.prisijungti(request.form['email'])
        else:
            error = 'Invalid username/password'
    # the code below is executed if the request method
    # was GET or the credentials were invalid
    return render_template('login.html', error=error)

@app.route('/signup/')
def signup():
    return render_template('signup.html')

# with app.test_request_context():
#     print (url_for(login))
#     print (url_for(mains))
#     print (url_for(signup))


app.run(host='0.0.0.0')