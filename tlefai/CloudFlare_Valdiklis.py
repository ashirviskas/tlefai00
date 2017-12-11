import requests
base_link="https://api.cloudflare.com/client/v4/user/"
def patikrinti_api_key(session, db, email, api_key):

    parameters = {"X-Auth-Email":email, "X-Auth-Key":api_key,  "Content-Type":"application/json"}

    response = requests.get( base_link, headers=parameters)
    print(response.text)
    if response.status_code == 200:
        print("Authorisation successful")
        sudeti_raktus_i_lentele(session, db, api_key, email)
        return True
    else:
        print("Authorisation error")
        return False
    return
def sudeti_raktus_i_lentele(session, db, api_key, email):
    cur = db.cursor()
    print(session['user_id'])
    try:
        cur.execute("""INSERT INTO CloudFlare_user (api_key, user_id, email) VALUES (%s,%s,%s)""",(api_key, int(session['user_id']), email))
        db.commit()
        print("Added key to db successfully")
    except:
        print("Failed adding to database")
        return False
    return

def pasirinkti_preset():
    return
def patvirtinti():
    return
def prideti_i_statistika():
    return
