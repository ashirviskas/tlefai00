import requests
base_link="https://api.cloudflare.com/client/v4/user/"
def patikrinti_api_key(email, api_key):

    parameters = {"X-Auth-Email":email, "X-Auth-Key":api_key,  "Content-Type":"application/json", "first_name":"John"}

    response = requests.request("PATCH", base_link, headers=parameters)
    print(response.text)
    if response.status_code == 200:
        print("Authorisation successful")
        return True
    else:
        print("Authorisation error")
        return False
    return
def sudeti_raktus_i_lentele():
    return

def pasirinkti_preset():
    return
def patvirtinti():
    return
def prideti_i_statistika():
    return
