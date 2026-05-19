import requests
import time
import json

url = "https://www.tesla.com/pt_pt/inventory/api/v1/inventory-results"

payload = {
    "query": {
        "model": "my",
        "condition": "new",
        "options": {},
        "arrangeby": "Price",
        "order": "asc",
        "market": "PT",
        "language": "pt",
        "super_region": "north america",
        "lng": -8.0,
        "lat": 39.5,
        "zip": "1000-001",
        "range": 0
    },
    "offset": 0,
    "count": 10,
    "outsideOffset": 0,
    "outsideSearch": False
}

headers = {
    "User-Agent": "Mozilla/5.0",
    "Content-Type": "application/json"
}

while True:
    try:
        response = requests.post(url, headers=headers, json=payload)

        print(response.status_code)

        data = response.json()

        results = data.get("results", [])

        print(f"Carros encontrados: {len(results)}")

        for car in results:
            print(car.get("VIN"))

    except Exception as e:
        print("Erro:", e)

    time.sleep(60)
