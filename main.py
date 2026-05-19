import requests
import time
import os

print("BOT ARRANCOU", flush=True)

TELEGRAM_TOKEN = "8959555460:AAGEXGzl4ryc3VSNQKJhHl5SRvXTX32SrNk"
TELEGRAM_CHAT_ID = "-1003746876578"

REFERRAL = "joo39173"
SEEN_FILE = "seen.txt"

MODELS = [
    "m3",
    "my",
    "ms",
    "mx"
]


def load_seen():

    if not os.path.exists(SEEN_FILE):
        return set()

    with open(SEEN_FILE, "r") as f:
        return set(line.strip() for line in f if line.strip())


def save_seen(vin):

    with open(SEEN_FILE, "a") as f:
        f.write(vin + "\n")


def send_telegram(msg):

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": msg
    }

    response = requests.post(url, data=data)

    print("Telegram:", response.status_code, flush=True)


seen = load_seen()

print(f"VINs já conhecidos: {len(seen)}", flush=True)


headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json"
}


while True:

    try:

        total = 0

        for model in MODELS:

            try:

                url = f"https://www.tesla.com/inventory/api/v1/inventory-results?query={{\"query\":{{\"model\":\"{model}\",\"condition\":\"new\",\"options\":{{}},\"arrangeby\":\"plh\",\"order\":\"asc\",\"market\":\"PT\",\"language\":\"pt\",\"super_region\":\"north america\",\"lng\":\"-8.0\",\"lat\":\"39.5\",\"zip\":\"1000-000\",\"range\":0}},\"offset\":0,\"count\":24,\"outsideOffset\":0,\"outsideSearch\":false}}"

                print(f"A pedir {model}...", flush=True)

                r = requests.get(
                    url,
                    headers=headers,
                    timeout=30
                )

                print(f"Status: {r.status_code}", flush=True)

                data = r.json()

                results = data.get("results", [])

                print(f"{model}: {len(results)} carros", flush=True)

                total += len(results)

                for car in results:

                    vin = car.get("VIN")

                    if vin and vin not in seen:

                        seen.add(vin)

                        save_seen(vin)

                        link = f"https://www.tesla.com/pt_PT/my/order/{vin}?referral={REFERRAL}"

                        msg = f"""
🚗 Novo Tesla encontrado!

Modelo: {model.upper()}

{link}
"""

                        print(msg, flush=True)

                        send_telegram(msg)

            except Exception as e:

                print(f"Erro modelo {model}:", e, flush=True)

        print(f"TOTAL: {total} carros", flush=True)

        print("A aguardar 5 minutos...\n", flush=True)

        time.sleep(300)

    except Exception as e:

        print("Erro geral:", e, flush=True)

        time.sleep(60)
