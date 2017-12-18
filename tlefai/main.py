
from flask import Flask, url_for, redirect
from flask import render_template
from flask import request
from flask import session
import MySQLdb, requests


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
            return render_template("confirmCloudFlareAPIKeys.html", error="ServerPilot API keys confirmed!")
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
            return render_template("confirmServerpilotAPIKeys.html", error="DigitalOcean keys confirmed")
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
        preset_id = request.form.get('preset_id')
        print(preset_id)
        pasirinkti_preset(preset_id)
        return redirect("/confirmDigitalOceanAPIKeys/")
    return render_template("preset_selection.html", presets=presets)


@app.route('/configureDigitalOcean/', methods=['POST', 'GET'])
def configureDigitalOcean():
    error = None
    cur = db.cursor()
    cur.execute("SELECT api_key FROM DigitalOcean_user WHERE user_id=%s ORDER BY ID DESC", str(session['user_id']))
    api_key = cur.fetchall()[0][0]
    headers = {"Content-Type": "application/json", "Authorization": "Bearer " + api_key}

    api_link = 'https://api.digitalocean.com/v2/regions'
    response = requests.get(api_link, headers=headers)
    response_data = response.json()
    regionoptions = []
    for value in response_data["regions"]:
        regionoptions.append("<option value='" + value["slug"] + "'>" + value["name"] + "</option>")

    api_link = 'https://api.digitalocean.com/v2/images?type=distribution'
    response = requests.get(api_link, headers=headers)
    response_data = response.json()
    imageoptions = []
    for value in response_data["images"]:
        imageoptions.append("<option value='" + value["slug"] + "'>" + value["distribution"] + " " + value["name"] + "</option>")

    api_link = 'https://api.digitalocean.com/v2/sizes'
    response = requests.get(api_link, headers=headers)
    response_data = response.json()
    sizeoptions = []
    for value in response_data["sizes"]:
        sizeoptions.append("<option value='" + value["slug"] + "'>" + value["slug"] + "</option>")

    # api_link = 'https://api.digitalocean.com/v2/volumes'
    # response = requests.get(api_link, headers=headers)
    # response_data = response.json()
    # volumeoptions = []
    # for value in response_data["volumes"]:
    #     volumeoptions.append("<option value='" + value["id"] + "'>" + value["name"] + " " + value["size_gigabytes"] + " GB" + "</option>")

    ####open the html template file, read it into 'content'
    html_file = "./templates/configureDigitalOcean.html"
    f = open(html_file, 'r')
    content = f.read()
    f.close()

    ####replace the place holder with your python-generated list
    content = content.replace("$regionoptions", '\n'.join(regionoptions))
    content = content.replace("$imageoptions", '\n'.join(imageoptions))
    content = content.replace("$sizeoptions", '\n'.join(sizeoptions))
    # content = content.replace("$volumeoptions", '\n'.join(volumeoptions))

    ####write content into the final html
    output_html_file = "./templates/configureDigitalOceantemp.html"
    f = open(output_html_file, 'w')
    f.write(content)
    f.close()

    if request.method == 'POST':
        if DigitalOcean_valdiklis.patvirtinti(session, db, request.form):
            print("Data saved")
            # return render_template('index.html', error="Registration success!")
        else:
            error = 'Something went wrong'
    return render_template("configureDigitalOceantemp.html", error=error)


@app.route('/configureServerPilot/', methods=['POST', 'GET'])
def configureServerPilot():
    error = None
    preset = None
    preset_id = 1 #session.get("preset_id")
    runtimes = []
    runtimes.append("php5.4")
    runtimes.append("php5.5")
    runtimes.append("php5.6")
    runtimes.append("php7.0")
    runtimes.append("php7.1")
    runtimes.append("php7.2")
    if (preset_id is not None):
        preset = ServerPilot_valdiklis.parinkti_preset(db, preset_id)
        print(preset)
    if request.method == 'POST':
        if ServerPilot_valdiklis.patvirtinti(session, db, request.form):
            print("Data saved")
            # return render_template('index.html', error="Registration success!")
        else:
            error = 'Something went wrong'
    return render_template("configureServerPilot.html", error=error, preset = preset, runtimes = runtimes)



@app.route('/configureCloudFlare/', methods=['POST', 'GET'])
def configure_CloudFlare():
    preset_id = 28# session.get("preset_id")

    if (preset_id is not None):
        preset = CloudFlare_Valdiklis.parinkti_preset(db, preset_id)

        print("%s",preset)
    cur = db.cursor()
    cur.execute("SELECT * FROM CloudFlare_user WHERE user_id=%s ORDER BY ID DESC", str(session['user_id']))
    data = cur.fetchall()
    api_key = data[0][1]
    email = data[0][3]
    CloudFlare_Valdiklis.siusti_parinktis_i_API(session, db)
    error = None
    if request.method == 'POST':
        if CloudFlare_Valdiklis.patvirtinti(session, db, request.form):

            return render_template('index.html', error="Registration success!")
        else:
            error = 'Invalid username/password'
    return render_template("configureCloudFlare.html", error=error)


@app.route('/begin/')
def begin():
    return render_template("begin.html")


app.secret_key = 'thisforloggingin' #secret phrase for session
app.run(host='0.0.0.0')