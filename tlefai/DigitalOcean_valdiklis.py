import requests, time
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
    api_key = cur.fetchall()[0][0]
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
    siusti_parinktis_i_API(session, db) #temporary here for testing
    return True

def prideti_i_statistika(session, db, data):
    backups = 0
    if (data.get('backups') is not None):
        backups = 1
    ipv6 = 0
    if (data.get('ipv6') is not None):
        ipv6 = 1
    private_networking = 0
    if (data.get('private_networking') is not None):
        private_networking = 1
    monitoring = 0
    if (data.get('monitoring') is not None):
        monitoring = 1

    cur = db.cursor()
    if data['volumename'] != "" and data['volumesize'] != "":
        try:
            cur.execute("""INSERT INTO DigitalOcean_preset_volumes (volumesize, volumename) 
                           VALUES (%s,%s)""",(data['volumesize'], data['volumename']))
            db.commit()
        except:
            print("Failed adding to database")
            return False

        cur.execute("SELECT volumeid FROM DigitalOcean_preset_volumes ORDER BY volumeID DESC"),
        last_inserted_id = cur.fetchall()[0][0]
    else:
        last_inserted_id = None

    try:
         cur.execute("""INSERT INTO DigitalOcean_preset (name, region, size, image, backups, ipv6, private_networking, 
          monitoring, tags, userdata, volumeid) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",(data['name'],data['region'],data['size'],
                                                                    data['image'],backups,ipv6,
                                                                    private_networking,monitoring,
                                                                    data['tags'],data['userdata'], last_inserted_id))
         db.commit()
    except:
        print("Failed adding to database")
        return False

    cur.execute("SELECT presetId FROM DigitalOcean_preset ORDER BY presetID DESC")
    last_inserted_id = cur.fetchall()[0][0]

    try:
        cur.execute("""INSERT INTO Chosen_Preset (userid, digitaloceanid, date_of_selection) 
                       VALUES (%s,%s,%s)""",(str(session['user_id']), last_inserted_id, strftime("%Y-%m-%d %H:%M:%S", gmtime())))
        db.commit()
    except:
        print("Failed adding to database")
        return False

    cur.execute("SELECT chosenID FROM Chosen_Preset WHERE userid = %s ORDER BY chosenID DESC",
                str(session['user_id']))
    session['chosen_id'] = cur.fetchall()[0][0]
    return True


def parinkti_preset(session, db):
    cur = db.cursor()
    cur.execute("SELECT dp.*, dpv.volumesize, dpv.volumename FROM DigitalOcean_preset dp LEFT JOIN Preset p ON (p.digitaloceanID=dp.presetid) "
                "LEFT JOIN DigitalOcean_preset_volumes dpv ON (dpv.volumeid=dp.volumeid) "
                "WHERE p.presetID = %s", str(session['preset_id']))
    preset = cur.fetchone()
    data = {}
    description = cur.description
    for i in range(len(description)):
        data[description[i][0]]=preset[i]
    print(data)
    return data


def siusti_parinktis_i_API(session, db):
    cur = db.cursor()
    cur.execute("SELECT api_key FROM DigitalOcean_user WHERE user_id=%s ORDER BY ID DESC", str(session['user_id']))
    api_key = cur.fetchall()[0][0]

    cur.execute("SELECT dp.*, dpv.volumesize, dpv.volumename FROM DigitalOcean_preset dp LEFT JOIN Chosen_Preset cp ON "
                "(cp.digitaloceanID = dp.presetID) LEFT JOIN DigitalOcean_preset_volumes dpv ON (dpv.volumeid=dp.volumeid) "
                "WHERE cp.userid=%s ORDER BY presetID DESC", str(session['user_id']))
    data = cur.fetchone()

    cur.execute("SELECT dd.fingerprint FROM DigitalOcean_droplet dd LEFT JOIN DigitalOcean_user du ON "
                "(dd.user_id = du.id) WHERE du.user_id=%s ORDER BY droplet_ID DESC", str(session['user_id']))
    sshkey = cur.fetchone()[0]

    api_link = 'https://api.digitalocean.com/v2/droplets'
    api_data = {"name":data[1],"region":data[2],"size":data[3],"image":data[4],
                "ssh_keys": [sshkey],"backups":data[5]!=0,"ipv6":data[6]!=0,"private_networking":data[7]!=0, "monitoring":data[8]!=0,
                "tags":str(data[9]).split() ,"userdata": data[10]}
    headers = {"Content-Type": "application/json", "Authorization": "Bearer " + api_key}
    response = requests.post(api_link, headers=headers, json=api_data)
    if response.status_code == 202:
        print("Droplet successfully created")
        droplet_data = response.json()
    else:
        print(str(response.text))
        return False

    if data[12] is not None and data[13] is not None:
        api_link = 'https://api.digitalocean.com/v2/volumes'
        api_data = {"size_gigabytes":data[12], "name": data[13], "description": "", "region": data[2]}
        response = requests.post(api_link, headers=headers, json=api_data)
        if response.status_code == 201:
            print("Volume successfully created, waiting for 15 seconds to attach")
            time.sleep(15)
            api_link = 'https://api.digitalocean.com/v2/volumes/actions'
            api_data = {"type": "attach", "volume_name": data[13], "region": data[2], "droplet_id": droplet_data["droplet"]["id"]}
            response = requests.post(api_link, headers=headers, json=api_data)
            if response.status_code == 202:
                print("Volume successfully attached")
            else:
                print(str(response.text))
        else:
            print(str(response.text))

    return True

