from playwright.sync_api import sync_playwright
import requests
import time
import os
import re
import json

print("BOT ARRANCOU", flush=True)

TELEGRAM_TOKEN = "8959555460:AAGEXGzl4ryc3VSNQKJhHl5SRvXTX32SrNk"
TELEGRAM_CHAT_ID = "-1003746876578"

REFERRAL = "joo39173"
SEEN_FILE = "seen.txt"

TESLA_URL = "https://www.tesla.com/pt_PT/inventory/new/my?arrangeby=plh&zip=1000-000&range=0"


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

    print("Telegram:", response.status_code, flush=True)


seen = load_seen()

print(f"VINs já conhecidos: {len(seen)}", flush=True)


while True:

    try:

        print("A abrir Tesla...", flush=True)

        with sync_playwright() as p:

            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-blink-features=AutomationControlled"
                ]
            )

            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                           "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
                viewport={"width": 1366, "height": 768},
                locale="pt-PT"
            )

            page = context.new_page()

            page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            })
            """)

            page.goto(
                TESLA_URL,
                wait_until="domcontentloaded",
                timeout=60000
            )

            page.wait_for_timeout(15000)

            html = page.content()

            browser.close()

        vins = re.findall(r'5YJ[a-zA-Z0-9]{14}', html)

        cars = list(set(vins))

        print(f"Encontrados {len(cars)} carros", flush=True)

        for vin in cars:

            if vin not in seen:

                seen.add(vin)

                save_seen(vin)

                link = f"https://www.tesla.com/pt_PT/my/order/{vin}?referral={REFERRAL}"

                msg = f"""
🚗 Novo Tesla encontrado!

{link}
"""

                print(msg, flush=True)

                send_telegram(msg)

        print("A aguardar 5 minutos...\n", flush=True)

        time.sleep(300)

    except Exception as e:

        print("Erro:", e, flush=True)

        time.sleep(60)
