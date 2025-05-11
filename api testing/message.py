import requests

access_token = ""
page_id = ""

url = f"https://graph.facebook.com/v22.0/{579541655252610}/conversations"
params = {
    "access_token": access_token
}

response = requests.get(url, params=params)
print(response.json())
