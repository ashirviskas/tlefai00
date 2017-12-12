import requests

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
    cur = db.cursor()
    cur.execute("SELECT sp.*, spw.* FROM ServerPilot_preset sp "
                "LEFT JOIN ServerPilot_preset_wordpress spw ON spw.wordpress_presetID = sp.serverpilot_presetID"
                " WHERE sp.presetID=%s", str(preset_id))
    preset = cur.fetchone()
    print(preset)
    return preset


def siusti_parinktis_i_API(session, db):
    cur = db.cursor()
    cur.execute("SELECT api_key FROM ServerPilot_user WHERE user_id=%s ORDER BY ID DESC", str(session['user_id']))
    api_key = cur.fetchall()[0][1]
    client_id = cur.fetchall()[0][3]
    print(api_key, client_id)


def prideti_i_statistika():
    return
