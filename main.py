from playwright.sync_api import sync_playwright
import requests
import time
import json
import re

TELEGRAM_TOKEN = "8959555460:AAGEXGzl4ryc3VSNQKJhHl5SRvXTX32SrNk"
TELEGRAM_CHAT_ID = "-1003746876578"

seen = set()

def send_telegram(msg):

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": msg
    }

    requests.post(url, data=data)

while True:

    try:

        with sync_playwright() as p:

            browser = p.chromium.launch(headless=True)

            page = browser.new_page()

            page.goto(
                "https://www.tesla.com/pt_PT/inventory/new/my?arrangeby=plh&zip=1000-000&range=0"
            )

            page.wait_for_timeout(5000)

            content = page.content()

            browser.close()

        cars = re.findall(r'"/my/order/([^"]+)"', content)

        for vin in cars:

            if vin not in seen:

                seen.add(vin)

                link = f"https://www.tesla.com/pt_PT/my/order/{vin}?referral=joo39173"

                msg = f"""
🚗 Novo Tesla encontrado!

{link}
"""

                print(msg)

                send_telegram(msg)

        print(f"Encontrados {len(cars)} carros")

        time.sleep(300)

    except Exception as e:

        print("Erro:", e)

        time.sleep(60)
