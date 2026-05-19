import requests
import time

TELEGRAM_TOKEN = "8959555460:AAGEXGzl4ryc3VSNQKJhHl5SRvXTX32SrNk"
TELEGRAM_CHAT_ID = "-1003746876578"

REFERRAL_LINK = "https://www.tesla.com/pt_pt/referral/joo39173"

seen = set()

headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json"
}

def send_telegram(msg):

    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": msg
    }

    requests.post(telegram_url, data=data)

while True:

    try:

        response = requests.get(
            "https://www.tesla.com/inventory/api/v1/inventory-results",
            headers=headers,
            params={
                "query": '{"model":"my","condition":"new","market":"PT","language":"pt","super_region":"europe","zip":"1000-000","range":0,"arrangeby":"Price","order":"asc"}'
            }
        )

        print(response.status_code)

        data = response.json()

        results = data.get("results", [])

        print(f"Encontrados {len(results)} carros")

        for car in results:

            vin = car.get("VIN")

            if vin not in seen:

                seen.add(vin)

                model = car.get("TrimName")
                price = car.get("PurchasePrice")

                link = f"https://www.tesla.com/pt_PT/my/order/{vin}?referral=joo39173"

                msg = f"""
🚗 Novo Tesla encontrado!

Modelo: {model}

Preço: €{price}

Link:
{link}
"""

                print(msg)

                send_telegram(msg)

        time.sleep(300)

    except Exception as e:

        print("Erro:", e)

        time.sleep(60)
