import requests, json
from cryptography.hazmat.primitives import serialization as crypto_serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend as crypto_default_backend
from random import randint


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
        cur.execute("""INSERT INTO DigitalOcean_user (api_key, user_id) VALUES (%s,%s)""",(api_key, session['user_id']))
        db.commit()
    except:
        print("Failed adding to database")
        return False
    return True


def generuoti_ssh_raktus(session, db):
    key = rsa.generate_private_key(
        backend=crypto_default_backend(),
        public_exponent=65537,
        key_size=2048
    )
    private_key = key.private_bytes(
        crypto_serialization.Encoding.PEM,
        crypto_serialization.PrivateFormat.PKCS8,
        crypto_serialization.NoEncryption())
    public_key = key.public_key().public_bytes(
        crypto_serialization.Encoding.OpenSSH,
        crypto_serialization.PublicFormat.OpenSSH
    )
    public_key = str(public_key)[2:-1]

    ideti_SSH_raktus(session, db, public_key, private_key)
    return True


def ideti_SSH_raktus(session, db, public_key, private_key):
    cur = db.cursor()
    cur.execute("SELECT api_key FROM DigitalOcean_user WHERE user_id=%s ORDER BY ID DESC", str(session['user_id']))
    print(public_key)
    api_key = cur.fetchall()[0][0]
    print(api_key)
    api_link = 'https://api.digitalocean.com/v2/account/keys'
    api_data = {"name": "tlefaitest", "public_key": public_key}
    headers = {"Content-Type": "application/json", "Authorization": "Bearer " + api_key}
    response = requests.post(api_link, params=api_data, headers=headers)
    if response.status_code == 201:
        response_data = response.json()
        print(str(response.text))
        fingerprint = response_data["ssh_key"]["fingerprint"]
        cur.execute("SELECT id FROM DigitalOcean_user WHERE user_id=%s ORDER BY ID DESC", str(session['user_id']))
        user_id = cur.fetchall()[0][0]
        try:
            cur.execute(
                """INSERT INTO DigitalOcean_droplet (fingerprint, ssh_key_public, ssh_key_private, user_id) 
                VALUES (%s,%s,%s,%s)""",
                (fingerprint, str(public_key), str(private_key), str(user_id)))
            db.commit()
        except:
            print("Failed adding to database")
            return False
    else:
        print("Failed to add SSH key to DigitalOcean account")
        return False
    return True


def patvirtinti():
    return True


def prideti_i_statistika():
    return True


def parinkti_preset():
    return True


def siusti_parinktis_i_API(session, db):
    cur = db.cursor()
    cur.execute("SELECT api_key FROM DigitalOcean_user WHERE user_id=%s ORDER BY ID DESC", str(session['user_id']))
    api_key = cur.fetchall()[0][0]

    api_link = 'https://api.digitalocean.com/v2/droplets'
    api_data = {"name":"example.com","region":"nyc3","size":"512mb","image":"ubuntu-14-04-x64","ssh_keys":"null",
                "backups":"false","ipv6":"true","user_data":"null","private_networking":"null","volumes": "null","tags":["web"]}
    headers = {"Content-Type": "application/json", "Authorization": "Bearer" + api_key}
    response = requests.post(api_link, headers=headers, data=api_data)
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


