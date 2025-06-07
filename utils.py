import requests

def get_sources():
    with open("proxy_sources.txt", "r") as f:
        return [url.strip() for url in f.readlines() if url.strip()]

async def fetch_socks5_proxies():
    sources = get_sources()
    proxies = set()
    for url in sources:
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                for line in resp.text.splitlines():
                    if ":" in line:
                        proxies.add(line.strip())
        except:
            pass
    return list(proxies)

def filter_by_location(data, query):
    return query.lower() in str(data.get("zip_code", "")).lower() or            query.lower() in str(data.get("region", "")).lower() or            query.lower() in str(data.get("country_code", "")).lower()
