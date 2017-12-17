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
def patvirtinti(session, db, data):
    prideti_i_statistika(session, db, data)
    #prideti_i_statistika_Firewall(session, db, data)
    #prideti_i_statistika_preset(session, db, data)



def prideti_i_statistika(session, db, data):
    cur = db.cursor()
    priority=data.get("priority")
    hosts=data.get("hosts")
    zone_id=data.get("zone_id")
    status=data.get("status")
    signature=data.get("signature")
    certificate=data.get("certificate")
    private_key=data.get("private_key")

    try:
        cur.execute("""INSERT INTO Cloudflare_preset_SSL (priority, hosts, zone_id, status, signature, certificate, private_key)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                    (priority, hosts, zone_id, status, signature, certificate, private_key))
        db.commit()
    except:
        print("Failed adding to database ssl")
        return False

    # firewall setting
    id = data.get("id")
    mode = data.get("mode")
    match = data.get("match")
    order = data.get("order")
    per_page = int(data.get("per_page"))
    configuration_target = data.get("configuration_target")
    direction = data.get("direction")
    value_adress = data.get("value_adress")
    value_range = data.get("value_range")
    value_country_code = data.get("value_country_code")
    try:
        cur.execute(
            """INSERT INTO Cloudflare_preset_Firewall (id, mode, match, order, per_page, configuration_target, direction, value_adress, value_range, value_country_code) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (id, mode, match, order, per_page, configuration_target, direction, value_adress, value_range, value_country_code))
        db.commit()
    except:
        print("Failed adding to database firewall")
        return False
    #DNS settings
    type = data.get("type")
    name = data.get("name")
    content = data.get("content")
    ttl = data.get("ttl")
    proxied = 0
    if (data.get('proxied') is not None):
        proxied = 1
    try:
        cur.execute("""INSERT INTO Cloudflare_preset (type, name, content, ttl, proxied) VALUES (%s, %s, %s, %s, %s)""",
                    (type, name, content, ttl, proxied))
        db.commit()
    except:
        print("Failed adding to database dns")
        return False


    return True

def pasirinkti_preset():
    return

