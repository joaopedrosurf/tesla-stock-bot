import requests
import time
import os
import re
from html import unescape

print("BOT ARRANCOU", flush=True)

TELEGRAM_TOKEN = "8959555460:AAGEXGzl4ryc3VSNQKJhHl5SRvXTX32SrNk"
TELEGRAM_CHAT_ID = "-1003746876578"

REFERRAL = "joo39173"
SEEN_FILE = "seen.txt"

TESLA_INFO_URL = "https://tesla-info.com/for-sale/Portugal/Any/New/?state=&miles=99999&max=9999999&year=20082026&sortsale=256&token=524288&spec=0&adv=0&minrange=0"


def load_seen():
    if not os.path.exists(SEEN_FILE):
        return set()

    with open(SEEN_FILE, "r") as f:
        return set(line.strip() for line in f if line.strip())


def save_seen(car_id):
    with open(SEEN_FILE, "a") as f:
        f.write(car_id + "\n")


def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": msg,
        "disable_web_page_preview": False
    }

    response = requests.post(url, data=data, timeout=20)

    print("Telegram:", response.status_code, flush=True)


def clean_text(text):
    text = re.sub(r"<.*?>", " ", text)
    text = unescape(text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


seen = load_seen()

print(f"Carros já conhecidos: {len(seen)}", flush=True)


while True:

    try:

        print("A consultar Tesla-info...", flush=True)

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(
            TESLA_INFO_URL,
            headers=headers,
            timeout=30
        )

        print("Status:", response.status_code, flush=True)

        html = response.text

        order_links = re.findall(
            r'https://www\.tesla\.com/pt_PT/[a-z0-9]+/order/[^"\s<]+',
            html
        )

        order_links = list(set(order_links))

        print(f"Encontrados {len(order_links)} carros", flush=True)

        for link in order_links:

            link = unescape(link)

            car_id = link.split("/order/")[-1].split("?")[0]

            if car_id not in seen:

                seen.add(car_id)
                save_seen(car_id)

                clean_link = link.split("?")[0]
                referral_link = f"{clean_link}?referral={REFERRAL}"

                msg = f"""
🚗 Novo Tesla encontrado!

{referral_link}
"""

                print(msg, flush=True)

                send_telegram(msg)

        print("A aguardar 5 minutos...\n", flush=True)

        time.sleep(300)

    except Exception as e:

        print("Erro geral:", e, flush=True)

        time.sleep(60)
