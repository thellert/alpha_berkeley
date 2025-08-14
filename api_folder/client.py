import requests

try:
    laptop_1_ip = "http://192.128.196.143:8000"

    response = requests.get(laptop_1_ip)
    print(response.json())

except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")