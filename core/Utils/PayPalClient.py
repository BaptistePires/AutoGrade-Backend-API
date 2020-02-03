import requests

url = 'https://api.sandbox.paypal.com/v2/checkout/orders/0WR15982TV1268109'

header = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer {token}'.format(token='A21AAEy_Fhyn2pN3WqqlH2Qzbt6Xd8Hl2UrFwmsKP9O93t-CB__z_IC6O4p1VNUJUoVTTrqhNd64Knh6_5ftHQ-kX6p46EmPw')
}

r = requests.get(url, headers=header)
print(r.content)