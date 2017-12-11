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
        public_exponent=randint(0, 999999),
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
    ideti_SSH_raktus(session, db, public_key, private_key)
    return True


def ideti_SSH_raktus(session, db, public_key, private_key):
    cur = db.cursor()
    print(private_key)
    cur.execute("SELECT id FROM DigitalOcean_user WHERE user_id=%s ORDER BY ID DESC", str(session['user_id']))
    user_id = cur.fetchall()[0][0]
    try:
        cur.execute("""INSERT INTO DigitalOcean_droplet (ssh_key_public, ssh_key_private, user_id) VALUES (%s,%s,%s)""",
                (str(public_key), str(private_key), str(user_id)))
        db.commit()
    except:
        print("Failed adding to database")
        return False
    return True


def patvirtinti():
    return True


def prideti_i_statistika():
    return True


def parinkti_preset():
    return True


def siusti_parinktis_i_API():
    return True


