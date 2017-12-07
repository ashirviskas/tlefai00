
from flask import Flask, url_for
from flask import render_template
from flask import request
import MySQLdb


from tlefai import kliento_autorizacijos_valdiklis



app = Flask(__name__)
DBpassword_ = open("database.txt", "r").readline()[:-1]
db = MySQLdb.connect(host="159.203.142.248", user="root", passwd=DBpassword_, db="tlefdatabase")

@app.route('/')
def mains():
    return render_template('index.html')

@app.route('/login/', methods=['POST', 'GET'])
def login():
    error = None
    if request.method == 'POST':
        if kliento_autorizacijos_valdiklis.patikrinti_duomenis(db, request.form['email'],
                       request.form['password']):
            print("Logged in success")
            return kliento_autorizacijos_valdiklis.prisijungti(db, request.form['email'])
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