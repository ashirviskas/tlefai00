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

    if(prideti_i_statistika(session,db,data)):

        return True
    else:
        return False

    # siusti_parinktis_i_API(session, db) #temporary here for testing

def parinkti_preset(db, preset_id):
    if preset_id is not None:
        cur = db.cursor()
        cur.execute("SELECT sp.*, spw.* FROM Cloudflare_preset sp "
                    "LEFT JOIN Cloudflare_preset_Firewall spw ON spw.presetID = sp.Cloudflare_preset_Firewall "
                    "LEFT JOIN Cloudflare_preset_SSL spw2 ON spw2.presetID = sp.Cloudflare_preset_SSL "
                    " WHERE sp.presetID="+ str(preset_id))
        preset = cur.fetchone()
        data = {}
        description = cur.description
        for i in range(len(description)):
            data[description[i][0]]=preset[i]
        return data
    return None

def prideti_i_statistika(session, db, data):
    cur = db.cursor()
    priority=int(data.get("priority"))
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
        cur.execute("""INSERT INTO Cloudflare_preset_Firewall (id, mode_firewall, match_firewall, order_firewall, per_page, configuration_target, direction, value_adress, value_range, value_country_code) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (id, mode, match, order, per_page, configuration_target, direction, value_adress, value_range, value_country_code))
        db.commit()
    except:
        print("Failed adding to database firewall")
        return False
    # DNS settings
    type = data.get("type")
    name = data.get("name")
    content = data.get("content")
    ttl = int(data.get("ttl"))
    proxied = 0
    if (data.get('proxied') is not None):
        proxied = 1
    try:
        cur.execute("SELECT presetID FROM Cloudflare_preset_Firewall ORDER BY presetID DESC")
        last_inserted_id_firewall = cur.fetchall()[0][0]
        cur.execute("SELECT presetID FROM Cloudflare_preset_SSL ORDER BY presetID DESC")
        last_inserted_id_ssl = cur.fetchall()[0][0]
        cur.execute("""INSERT INTO Cloudflare_preset (type_dns, name_dns, content, ttl, proxied, CloudFlare_preset_SSL, Cloudflare_preset_Firewall ) VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                    (type, name, content, ttl, proxied, last_inserted_id_ssl, last_inserted_id_firewall))
        db.commit()
    except:
        print("Failed adding to database dns")
        return False


    return True

def siusti_parinktis_i_API(session, db):
    cur = db.cursor()
    cur.execute("SELECT * FROM CloudFlare_user WHERE user_id=%s ORDER BY ID DESC", str(session['user_id']))
    data = cur.fetchall()
    # print(data)
    api_key = data[0][1]
    email = data[0][3]
    cur.execute("SELECT clp.*, cpf.id, cpf.mode_firewall, cpf.match_firewall, cpf.order_firewall, cpf.per_page, cpf.configuration_target, cpf.direction, cpf.value_adress, cpf.value_range, cpf.value_country_code, "
                "cps.priority, cps.hosts, cps.zone_id, cps.status, cps.signature, cps.certificate, cps.private_key "
                "FROM Cloudflare_preset clp LEFT JOIN Chosen_Preset cp ON "
                "(cp.cloudflareID = clp.presetID) LEFT JOIN Cloudflare_preset_Firewall cpf ON (cpf.presetID=clp.Cloudflare_preset_Firewall) "
                "LEFT JOIN Cloudflare_preset_SSL cps ON (cps.presetID=clp.Cloudflare_preset_SSL) "
                "WHERE cp.userid=" + str(session['user_id']) +" ORDER BY presetID DESC" )
    data = cur.fetchone()
    proxied = False
    if(data[5] == 1):
        proxied = True

    api_link = "https://api.cloudflare.com/client/v4/zones/023e105f4ecef8ad9ca31a8372d0c353/dns_records"
    api_data = {"type": data[1], "name": data[2], "content": data[3], "ttl": int(data[4]), "proxied": proxied}
    header = {"X-Auth-Email": email, "X-Auth-Key": api_key, "Content-Type": "application/json"}
    dnsresponse = requests.post(api_link, headers=header, json=api_data)

    print("dns response")
    print(dnsresponse)

    api_link = "https://api.cloudflare.com/client/v4/zones/023e105f4ecef8ad9ca31a8372d0c353/custom_certificates"
    api_data = {"certificate":data[20],"private_key":data[21]}
    header = {"X-Auth-Email": email, "X-Auth-Key": api_key, "Content-Type": "application/json"}
    certificateresponse = requests.post(api_link, headers=header, json=api_data)

    print("dns certificate response")
    print(certificateresponse)

    api_link = "https://api.cloudflare.com/client/v4/zones/023e105f4ecef8ad9ca31a8372d0c353/custom_certificates?status=active&page=1&per_page=20&order=status&direction=desc&match=all"
    api_data = {"status":data[19]}
    header = {"X-Auth-Email": email, "X-Auth-Key": api_key, "Content-Type": "application/json"}
    status = requests.get(api_link, headers=header, json=api_data)

    print("dns status response")
    print(status)

    api_link = "https://api.cloudflare.com/client/v4/zones/023e105f4ecef8ad9ca31a8372d0c353/firewall/access_rules/rules?scope_type=zone&mode=challenge&configuration_target=ip&configuration_value=1.2.3.4&notes=mynote&page=1&per_page=50&order=scope_type&direction=desc&match=all"
    api_data = {"mode":data[7],"match":data[8],"order":data[9],"per_page":data[10],"configuration_target":data[11],"direction":data[12]}
    header = {"X-Auth-Email": email, "X-Auth-Key": api_key, "Content-Type": "application/json"}
    firewallsettings = requests.get(api_link, headers=header, json=api_data)

    print("firewall setting response")
    print(firewallsettings)

    api_link = "https://api.cloudflare.com/client/v4/zones/023e105f4ecef8ad9ca31a8372d0c353/firewall/access_rules/rules"
    api_data= {"mode": data[7], "configuration": {"target": "ip", "value": data[13]}, "configuration": {"target":"ip_range", "value":data[14]}, "configuration": {"target":"country", "value":data[15]}}
    firewall = requests.post(api_link, headers=header, json=api_data)

    print("firewall response")
    print(firewall)
    return