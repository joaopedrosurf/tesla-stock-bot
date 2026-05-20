from playwright.sync_api import sync_playwright
import requests
import time
import os
import re

print("BOT ARRANCOU NO MAC", flush=True)

TELEGRAM_TOKEN = "8959555460:AAGEXGzl4ryc3VSNQKJhHl5SRvXTX32SrNk"
TELEGRAM_CHAT_ID = "-1003746876578"

REFERRAL = "joo39173"
SEEN_FILE = "seen.txt"

TESLA_URLS = [
    ("Model 3", "https://www.tesla.com/pt_PT/inventory/new/m3?arrangeby=plh&zip=1000-000&range=0"),
    ("Model Y", "https://www.tesla.com/pt_PT/inventory/new/my?arrangeby=plh&zip=1000-000&range=0"),
    ("Model S", "https://www.tesla.com/pt_PT/inventory/new/ms?arrangeby=plh&zip=1000-000&range=0"),
    ("Model X", "https://www.tesla.com/pt_PT/inventory/new/mx?arrangeby=plh&zip=1000-000&range=0")
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
        "text": msg,
        "disable_web_page_preview": False
    }

    response = requests.post(url, data=data, timeout=20)
    print("Telegram:", response.status_code, flush=True)


seen = load_seen()
print(f"VINs já conhecidos: {len(seen)}", flush=True)


while True:
    try:
        all_cars = []

        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=False,
                args=[
                    "--disable-blink-features=AutomationControlled"
                ]
            )

            context = browser.new_context(
                viewport={"width": 1400, "height": 900},
                locale="pt-PT"
            )

            page = context.new_page()

            for model_name, url in TESLA_URLS:
                print(f"A abrir {model_name}...", flush=True)

                page.goto(url, wait_until="domcontentloaded", timeout=60000)
                page.wait_for_timeout(15000)

                html = page.content()

                vins = re.findall(r'[A-Z0-9]{5,}_[a-zA-Z0-9]{20,}', html)
                vins += re.findall(r'5YJ[a-zA-Z0-9]{14}', html)
                vins += re.findall(r'7SA[a-zA-Z0-9]{14}', html)

                vins = list(set(vins))

                print(f"{model_name}: encontrados {len(vins)} carros", flush=True)

                for vin in vins:
                    all_cars.append((model_name, vin))

            browser.close()

        print(f"TOTAL encontrados: {len(all_cars)}", flush=True)

        for model_name, vin in all_cars:
            if vin not in seen:
                seen.add(vin)
                save_seen(vin)

                if "_" in vin:
                    model_code = model_name.lower().replace("model ", "m")
                    link = f"https://www.tesla.com/pt_PT/{model_code}/order/{vin}?referral={REFERRAL}"
                else:
                    link = f"https://www.tesla.com/pt_PT/my/order/{vin}?referral={REFERRAL}"

                msg = f"""
🚗 Novo Tesla encontrado!

Modelo: {model_name}

{link}
"""

                print(msg, flush=True)
                send_telegram(msg)

        print("A aguardar 5 minutos...\n", flush=True)
        time.sleep(300)

    except Exception as e:
        print("Erro geral:", e, flush=True)
        time.sleep(60)
