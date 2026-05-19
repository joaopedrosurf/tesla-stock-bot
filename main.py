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
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }

    requests.post(url, data=data)

def check_tesla_stock():
    url = "https://www.tesla.com/inventory/api/v1/inventory-results"

    params = {
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
        "count": 20,
        "outsideOffset": 0,
        "outsideSearch": False
    }

    response = requests.post(url, json=params)

    data = response.json()

    if "results" not in data:
        print("Sem resultados.")
        return

    for car in data["results"]:
        vin = car["VIN"]

        if vin in sent_cars:
            continue

        sent_cars.add(vin)

        model = car.get("Model", "Tesla")
        price = car.get("TotalPrice", 0)

        link = f"https://www.tesla.com/pt_PT/my/order/{vin}"

        message = (
            f"🚗 <b>Novo Tesla em stock!</b>\n\n"
            f"Modelo: {model}\n"
            f"Preço: {price}€\n\n"
            f"🔗 {link}"
        )

        send_telegram_message(message)

        print(f"Enviado: {vin}")

while True:
    try:
        check_tesla_stock()
    except Exception as e:
        print("Erro:", e)

    time.sleep(300)
