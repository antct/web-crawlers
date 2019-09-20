import requests

username = ''
password = ''
image = ''

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36',
    'Connection': 'keep-alive'
}

data = {
    'client_id': '9a1fd200-8687-44b1-4c20-08d50a96e5cd',
    'client_secret': '8b53f727-08e2-4509-8857-e34bf92b27f2',
    'grant_type': 'password',
    'username': username,
    'password': password,
}

token_url = 'https://openid.cc98.org/connect/token'
resp = requests.post(url=token_url, data=data, headers=headers).json()
headers['authorization'] = '{} {}'.format(resp['token_type'], resp['access_token'])
headers['content-type'] = 'application/json'
gif_url = 'https://api-v2.cc98.org/me/portrait'
resp = requests.put(url=gif_url, data=bytes('"{}"'.format(image), encoding='utf-8'), headers=headers)
print('ok' if resp.status_code == 200 else 'fail')