from playwright.sync_api import sync_playwright
import requests
import time
import re
import os

TELEGRAM_TOKEN = "8959555460:AAGEXGzl4ryc3VSNQKJhHl5SRvXTX32SrNk"
TELEGRAM_CHAT_ID = "-1003746876578"

TESLA_URL = "https://www.tesla.com/pt_PT/inventory/new/my?arrangeby=plh&zip=1000-000&range=0"
REFERRAL = "joo39173"
SEEN_FILE = "seen.txt"


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
        "text": msg,
        "disable_web_page_preview": False
    }

    response = requests.post(url, data=data, timeout=20)

    print("Telegram:", response.status_code)
    print(response.text)


seen = load_seen()

print(f"VINs já conhecidos: {len(seen)}")


while True:

    try:

        print("A abrir site da Tesla...")

        with sync_playwright() as p:

            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-dev-shm-usage"
                ]
            )

            page = browser.new_page(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                           "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
            )

            page.goto(
                TESLA_URL,
                wait_until="networkidle",
                timeout=60000
            )

            page.wait_for_timeout(8000)

            content = page.content()

            browser.close()

        cars = re.findall(r'"/my/order/([^"]+)"', content)

        cars = list(set(cars))

        print(f"Encontrados {len(cars)} carros")

        for vin in cars:

            if vin not in seen:

                seen.add(vin)

                save_seen(vin)

                link = f"https://www.tesla.com/pt_PT/my/order/{vin}?referral={REFERRAL}"

                msg = f"""
🚗 Novo Tesla encontrado!

{link}
"""

                print(msg)

                send_telegram(msg)

        print("A aguardar 5 minutos...\n")

        time.sleep(300)

    except Exception as e:

        print("Erro:", e)

        time.sleep(60)
