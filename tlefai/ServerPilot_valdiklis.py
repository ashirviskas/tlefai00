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
    cur.execute("""INSERT INTO ServerPilot_user (api_key, user_id, client_id) VALUES (%s,%s,%s)""",(api_key, session['user_id'], client_id))
    db.commit()
    print("Added key to db successfully")
    # except:
    #     print("Failed adding to database")
    #     return False
    return

def pasirinkti_preset():
    return
def patvirtinti():
    return
def prideti_i_statistika():
    return
