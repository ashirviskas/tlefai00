
from flask import Flask, url_for, redirect
from flask import render_template
from flask import request
from flask import session
import MySQLdb


from tlefai import kliento_autorizacijos_valdiklis
from tlefai import kliento_registracijos_valdiklis
from tlefai import ServerPilot_valdiklis
from tlefai import DigitalOcean_valdiklis
from tlefai import CloudFlare_Valdiklis



app = Flask(__name__)
DBpassword_ = open("database.txt", "r").readline()[:-1]
db = MySQLdb.connect(host="159.203.142.248", user="root", passwd=DBpassword_, db="tlefdatabase")


def pasirinkti_preset(preset_id):
    session["preset_id"] = preset_id
    return


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
            print("Login success")

            if kliento_autorizacijos_valdiklis.prisijungti(db, request.form['email'], session):
                return render_template('begin.html')
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
            return redirect("/login/")
        else:
            error = 'Invalid username/password'
    # the code below is executed if the request method
    # was GET or the credentials were invalid
    return render_template('signup.html', error=error)

# with app.test_request_context():
#     print (url_for(login))
#     print (url_for(mains))
#     print (url_for(signup))


@app.route('/confirmServerpilotAPIKeys/', methods=['POST', 'GET'])
def confirmServerpilotAPIKeys():
    error = None
    if request.method == 'POST':
        api_key = request.form['api_key']
        client_id = request.form['client_id']
        if ServerPilot_valdiklis.patikrinti_api_key(session, db, api_key, client_id):
            return redirect("/confirmCloudFlareAPIKeys/")
        else:
            error = "Bad keys"
    return render_template("confirmServerPilotAPIKeys.html", error = error)


@app.route('/confirmDigitalOceanAPIKeys/', methods=['POST', 'GET'])
def confirmDigitalOceanAPIKeys():
    error = None
    if request.method == 'POST':
        api_key = request.form['api_key']
        if DigitalOcean_valdiklis.patikrinti_api_key(session, db, api_key):
            DigitalOcean_valdiklis.generuoti_ssh_raktus(session, db)
            return redirect("confirmServerpilotAPIKeys/")
        else:
            error = "Bad keys"
    return render_template("confirmDigitalOceanAPIKeys.html", error = error)


@app.route('/confirmCloudFlareAPIKeys/', methods=['POST', 'GET'])
def confirmCloudFlareAPIKeys():
    error = None
    if request.method == 'POST':
        api_key = request.form['api_key']
        email = request.form['email']
        if CloudFlare_Valdiklis.patikrinti_api_key(session, db, email, api_key ):
            return "Keys confirmed"
        else:
            error = "Bad keys"
    return render_template("confirmCloudFlareAPIKeys.html", error = error)


@app.route('/preset_selection/', methods=['POST', 'GET'])
def preset_selection():
    cur = db.cursor()
    cur.execute("SELECT * FROM Preset")
    presets_db = cur.fetchall()
    error = None
    presets = {}
    for preset in presets_db:
        presets[preset[0]]=preset[1]
    if request.method == 'POST':
        preset_id = request.form['preset_id']
        print(preset_id)
        pasirinkti_preset(preset_id)
    return render_template("preset_selection.html", presets=presets)


@app.route('/begin/')
def begin():
    return render_template("begin.html")


app.secret_key = 'thisforloggingin' #secret phrase for session
app.run(host='0.0.0.0')