import requests, json


def patikrinti_api_key(session, db, api_key):
    api_link = 'https://api.digitalocean.com/v2/account'
    headers= {"Authorization":"Bearer "+api_key}
    response = requests.get(api_link, headers=headers)
    print(response)
    if response.status_code == 200:
        print("Authorization successful")
        if ideti_API_rakta(session, db, api_key):
            print("Keys saved to database")
            return True
        else:
            print("Failed to save keys to database. Please try again")
            return False
    else:
        print("Authorization error")
        return False

def ideti_API_rakta(session, db, api_key):
    cur = db.cursor()
    try:
        cur.execute("""INSERT INTO DigitalOcean_user (api_key, user_id) VALUES (%s,%s)""",(api_key, session.user_id))
        db.commit()
    except:
        print("Failed adding to database")
        return False
    return True

def generuoti_ssh_raktus():
    return True

def ideti_SSH_raktus(publickey, privatekey):
    return True

def patvirtinti():
    return True

def prideti_i_statistika():
    return True

def parinkti_preset():
    return True

def siusti_parinktis_i_API():
    return True


