
from flask import Flask, url_for
from flask import render_template
from flask import request
from flask import session
import MySQLdb


from tlefai import kliento_autorizacijos_valdiklis
from tlefai import kliento_registracijos_valdiklis



app = Flask(__name__)
DBpassword_ = open("database.txt", "r").readline()[:-1]
db = MySQLdb.connect(host="159.203.142.248", user="root", passwd=DBpassword_, db="tlefdatabase")


@app.route('/')
def mains():
    return render_template('index.html')


@app.route('/logout/')
def logout():
    session.pop('user_id')
    session.pop('logged_in')
    return render_template('index.html')


@app.route('/login/', methods=['POST', 'GET'])
def login():
    error = None
    if request.method == 'POST':
        user_id = kliento_autorizacijos_valdiklis.patikrinti_duomenis(db, request.form['email'],
                       request.form['password'])
        if user_id is not None:
            print("Logged in success")

            if kliento_autorizacijos_valdiklis.prisijungti(db, request.form['email'], session):
                return render_template('index.html')
        else:
            error = 'Invalid username/password'
    # the code below is executed if the request method
    # was GET or the credentials were invalid
    return render_template('login.html', error=error)


@app.route('/signup/', methods=['POST', 'GET'])
def signup():
    error = None
    print("Signup page loaded")
    if request.method == 'POST':
        if kliento_registracijos_valdiklis.uzregistruoti_vartotoja(db, request.form['username'],request.form['email'],
                                                               request.form['password']):
            print("Registration in success")
            return kliento_autorizacijos_valdiklis.prisijungti(db, request.form['email'])
        else:
            error = 'Invalid username/password'
    # the code below is executed if the request method
    # was GET or the credentials were invalid
    return render_template('signup.html', error=error)

# with app.test_request_context():
#     print (url_for(login))
#     print (url_for(mains))
#     print (url_for(signup))


app.secret_key = 'thisforloggingin'
app.run(host='0.0.0.0')