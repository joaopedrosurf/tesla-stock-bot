import requests
import time

TELEGRAM_TOKEN = "8959555460:AAGEXGzl4ryc3VSNQKJhHl5SRvXTX32SrNk"
TELEGRAM_CHAT_ID = "-1003746876578"

seen = set()

headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json"
}

def send_telegram(msg):

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": msg
    }

    requests.post(url, data=data)

while True:

    try:

        url = "https://www.tesla.com/inventory/api/v1/inventory-results"

        payload = {
            "query": {
                "model": "my",
                "condition": "new",
                "market": "PT",
                "language": "pt",
                "super_region": "europe",
                "zip": "1000-000",
                "range": 0,
                "arrangeby": "Price",
                "order": "asc"
            }
        }

        response = requests.post(
            url,
            json=payload,
            headers=headers
        )

        print(response.status_code)

        data = response.json()

        results = data.get("results", [])

        print(f"Encontrados {len(results)} carros")

        for car in results:

            vin = car.get("VIN")

            if vin not in seen:

                seen.add(vin)

                link = f"https://www.tesla.com/pt_PT/my/order/{vin}?referral=joo39173"

                modelo = car.get("TrimName")
                preco = car.get("PurchasePrice")

                msg = f"""
🚗 Novo Tesla encontrado!

Modelo: {modelo}
Preço: €{preco}

Link:
{link}
"""

                print(msg)

                send_telegram(msg)

        time.sleep(300)

    except Exception as e:

        print("Erro:", e)

        time.sleep(60)
