import requests

BASE_URL = 'http://127.0.0.1:5000/Users/Login'

data =   {
  "email": "string",
  "password": "string"
}



r = requests.post(BASE_URL, json=data)
print(r.text)

url = 'https://www.w3schools.com/python/demopage.php'
myobj = {'somekey': 'somevalue'}

x = requests.post(url, data = myobj)

print(x.text)

