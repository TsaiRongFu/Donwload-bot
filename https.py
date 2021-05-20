import requests
userid = ""
URL = "https://api.line.me/v2/bot/profile/"+ userid
header = {'Authorization': 'Bearer ..........................'}
r = requests.get(URL, headers = header)

print(r.json()['userId'])