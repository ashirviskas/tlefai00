import requests
import json
import paramiko

api_link = 'https://api.serverpilot.io/v1/'


def patikrinti_api_key(session, db, api_key, client_id):
    response = requests.get(api_link+"servers", auth=(client_id, api_key))
    print(response)
    if response.status_code == 200:
        print("Authorisation successful")
        sudeti_raktus_i_lentele(session, db, api_key, client_id)
        return True
    else:
        print("Authorisation error")
        return False


def sudeti_raktus_i_lentele(session, db, api_key, client_id):
    cur = db.cursor()
    print(session['user_id'])
    try:
        cur.execute("""INSERT INTO ServerPilot_user (api_key, user_id, client_id) VALUES (%s,%s,%s)""",(api_key, int(session['user_id']), client_id))
        db.commit()
        print("Added key to db successfully")
    except:
        print("Failed adding to database")
        return False
    return


def parinkti_preset(db, preset_id):
    if preset_id is not None:
        cur = db.cursor()
        cur.execute("SELECT sp.*, spw.* FROM ServerPilot_preset sp "
                    "LEFT JOIN ServerPilot_preset_wordpress spw ON spw.wordpress_presetID = sp.serverpilot_presetID"
                    " WHERE sp.presetID=%s", str(preset_id))
        preset = cur.fetchone()
        data = {}
        description = cur.description
        for i in range(len(description)):
            data[description[i][0]]=preset[i]
        print(data)
        return data
    return None

def siusti_parinktis_i_API(session, db):
    cur = db.cursor()
    cur.execute("SELECT * FROM ServerPilot_user WHERE user_id=%s ORDER BY ID DESC", str(session['user_id']))
    data = cur.fetchall()
    # print(data)
    api_key = data[0][1]
    client_id = data[0][3]
    try:
        cur.execute("SELECT * FROM Chosen_Preset WHERE userID=%s ORDER BY date_of_selection DESC", str(session['user_id']))
        ServerPilot_preset_id = 1#cur.fetchone()[4] #1 works
        # print(ServerPilot_preset_id)
        cur.execute("SELECT sp.*, spw.* FROM ServerPilot_preset sp "
                    "LEFT JOIN ServerPilot_preset_wordpress spw ON spw.wordpress_presetID = sp.serverpilot_presetID"
                    " WHERE sp.presetID=%s", str(ServerPilot_preset_id))
        data_sp = cur.fetchone()
        data = {}
        description = cur.description
        for i in range(len(description)):
            data[description[i][0]] = data_sp[i]
        headers = {"Content-Type":"application/json"}
        data_to_send={}
        data_to_send["name"] = data["site_title"]
        data_to_send["id"] = str(data["serverpilot_presetID"])
        data_to_send["autouptades"] = "false"
        if (data["autoupdates"] == 1):
            data_to_send["autouptades"] = "true"
        print("Gettin response")
        print(data_to_send)
        response = requests.post(api_link+"servers",auth=(client_id, api_key),headers = headers, json=data_to_send)
        response_obj = json.loads(response.text)
        print(response.text)
        print(response_obj["data"]["id"])
        print(response)
    except:
        print("Some errors")
        return None
    print(data)
    return True



def patvirtinti(session, db):

    return siusti_parinktis_i_API(session, db)


def prideti_i_statistika(session, db, data):
    cur = db.cursor()
    autoupdates = 0
    if (data.get('autoupdates') is not None):
         autoupdates = 1
    username = data.get("username")
    password= data.get("password")
    sysuser= data.get("sysuser")
    runtime= data.get("runtime")
    domain= data.get("domain")
    admin_user= data.get("admin_user")
    site_title= data.get("site_title")
    admin_password= data.get("admin_password")
    admin_email= data.get("admin_email")
    firewall = 0
    if (data.get('firewall') is not None):
        firewall = 1
    deny_unknown_domains = 0
    if (data.get('deny_unknown_domains') is not None):
        deny_unknown_domains = 1

    try:
        cur.execute("""INSERT INTO ServerPilot_preset_wordpress (admin_user, site_title, admin_password, admin_email) VALUES (%s,%s,%s,%s)""",
                    (admin_user, site_title, admin_password, admin_email))
        db.commit()
    except:
        print("Failed adding to database")
        return False
    try:
        cur.execute("SELECT wordpress_presetID FROM ServerPilot_preset_wordpress ORDER BY wordpress_presetID DESC")
        last_inserted_id = cur.fetchall()[0][0]
        print(last_inserted_id)
        cur.execute(
        """INSERT INTO ServerPilot_preset (autoupdates, username, password, sysuser, runtime, domain, firewall, deny_unknown_domains, serverpilot_presetID) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
        (autoupdates, username, password, sysuser,runtime, domain, firewall,deny_unknown_domains, last_inserted_id))
    except:
        print("Failed adding to database")
        return False

    try:
        cur.execute("SELECT presetID FROM ServerPilot_preset ORDER BY presetID DESC")
        last_inserted_id = cur.fetchall()[0][0]
        print(last_inserted_id)
        cur.execute("""UPDATE Chosen_Preset SET serverpilotID=%s WHERE chosenID=%s""",
                    (str(last_inserted_id), str(1)))
        db.commit()
    except:
        print("Failed adding to database")
        return False
    return True
