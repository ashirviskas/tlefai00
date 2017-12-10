import requests

api_link = 'https://api.serverpilot.io/v1/'

def patikrinti_api_key(api_key, client_id):
    response = requests.get(api_link+"servers", auth=(client_id, api_key))
    print(response)
    if response.status_code == 200:
        print("Authorisation successful")
        return True
    else:
        print("Authorisation error")
        return False
def sudeti_raktus_i_lentele():
    return

def pasirinkti_preset():
    return
def patvirtinti():
    return
def prideti_i_statistika():
    return
