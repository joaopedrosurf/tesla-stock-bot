import requests
import time
import os

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

sent_cars = set()

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    data = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }

    requests.post(url, data=data)

def check_tesla_stock():

    url = "https://www.tesla.com/inventory/api/v4/inventory-results"

    payload = {
        "query": {
            "model": "my",
            "condition": "new",
            "arrangeby": "Price",
            "order": "asc",
            "market": "PT",
            "language": "pt",
            "super_region": "north america",
            "zip": "1000-001",
            "range": 0
        },
        "offset": 0,
        "count": 10
    }

    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)

    print(response.text)

    data = response.json()

    results = data.get("results", [])

    for car in results:

        vin = car.get("VIN")

        if not vin:
            continue

        if vin in sent_cars:
            continue

        sent_cars.add(vin)

        price = car.get("TotalPrice", 0)

        model = car.get("Model", "Tesla")

        link = f"https://www.tesla.com/pt_PT/my/order/{vin}"

        message = (
            f"🚗 <b>Novo Tesla em stock!</b>\n\n"
            f"Modelo: {model}\n"
            f"Preço: {price}€\n\n"
            f"{link}"
        )

        send_telegram_message(message)

        print("Enviado:", vin)

while True:

    try:
        check_tesla_stock()

    except Exception as e:
        print("Erro:", e)

    time.sleep(300)
