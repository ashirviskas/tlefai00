import requests, json
from cryptography.hazmat.primitives import serialization as crypto_serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend as crypto_default_backend
from time import gmtime, strftime


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


def patvirtinti(session, db, data):
    prideti_i_statistika(session, db, data)


def prideti_i_statistika(session, db, data):
    cur = db.cursor()
    try:
        cur.execute("""INSERT INTO DigitalOcean_preset (name, region, size, image, backups, ipv6, private_networking, 
        volumes, monitoring, tags) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",(data['name'],data['region'],data['size'],
                                                                        data['image'],data['backups'],data['ipv6'],
                                                                        data['private_networking'],data['volumes'],
                                                                        data['monitoring'],data['tags']))
        db.commit()
    except:
        print("Failed adding to database")
        return False

    cur.execute("SELECT presetId FROM DigitalOcean_preset ORDER BY ID DESC")
    last_inserted_id = cur.fetchall()[0][0]

    try:
        cur.execute("""INSERT INTO Chosen_preset (userid, digitaloceanid, date_of_selection) 
                       VALUES (%s,%s,%s)""",(str(session['user_id']), last_inserted_id, strftime("%Y-%m-%d %H:%M:%S",                                                                              gmtime())))
        db.commit()
    except:
        print("Failed adding to database")
        return False

    cur.execute("SELECT chosenID FROM Chosen_preset WHERE userid = %s ORDER BY chosenID DESC",
                str(session['user_id']))
    session['chosen_id'] = cur.fetchall()[0][0]
    return True


def parinkti_preset(session, db):
    cur = db.cursor()
    cur.execute("SELECT dp.* FROM DigitalOcean_preset dp LEFT JOIN Preset p WHERE p.id = ", str(session['preset_id']))
    return cur.fetchall()


def siusti_parinktis_i_API(session, db):
    cur = db.cursor()
    cur.execute("SELECT api_key FROM DigitalOcean_user WHERE user_id=%s ORDER BY ID DESC", str(session['user_id']))
    api_key = cur.fetchall()[0][0]

    cur.execute("SELECT TOP 1 dp.* FROM DigitalOcean_preset dp LEFT JOIN Chosen_preset cp ON "
                "(cp.digitaloceanID = dp.presetID) WHERE user_id=%s ORDER BY ID DESC", str(session['user_id']))
    data = cur.fetchone()

    api_link = 'https://api.digitalocean.com/v2/droplets'
    api_data = {"name":data['name'],"region":data['region'],"size":data['size'],"image":data['image'],
                "ssh_keys":data['ssh_keys'],"backups":data['backups'],"ipv6":data['ipv6'],"user_data":data['user_data'],
                "private_networking":data['private_networking'],"volumes": data['volumes'],"tags":data['tags']}
    headers = {"Content-Type": "application/json", "Authorization": "Bearer " + api_key}
    response = requests.post(api_link, headers=headers, params=api_data)
    if response.status_code == 202:
        print("Droplet successfully created")
        return True
    else:
        print(str(response.text))
        return False


