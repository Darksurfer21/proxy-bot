import requests

def check_ip(ip, api_key):
    url = f"https://www.ipqualityscore.com/api/json/ip/{api_key}/{ip}"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            return r.json()
    except:
        return None
