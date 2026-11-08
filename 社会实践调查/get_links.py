import urllib.request, re
url = 'http://www.harryganzeboom.nl/isco08/index.htm'
try:
    with urllib.request.urlopen(url, timeout=10) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
    for link in re.findall(r'href=[\'"](.*?)[\'"]', html):
        if any(ext in link.lower() for ext in ['.txt', '.do', '.sps', '.pdf', '.csv', '.dta', 'isei']):
            print(link)
except Exception as e:
    print('Error:', e)
