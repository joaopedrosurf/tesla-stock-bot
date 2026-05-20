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
    ("Model 3", "m3", "https://www.tesla.com/pt_PT/inventory/new/m3?arrangeby=plh&zip=1000-000&range=0"),
    ("Model Y", "my", "https://www.tesla.com/pt_PT/inventory/new/my?arrangeby=plh&zip=1000-000&range=0"),
    ("Model S", "ms", "https://www.tesla.com/pt_PT/inventory/new/ms?arrangeby=plh&zip=1000-000&range=0"),
    ("Model X", "mx", "https://www.tesla.com/pt_PT/inventory/new/mx?arrangeby=plh&zip=1000-000&range=0")
]


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


seen = load_seen()
print(f"Carros já conhecidos: {len(seen)}", flush=True)


while True:
    try:
        all_cars = []

        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=False,
                args=["--disable-blink-features=AutomationControlled"]
            )

            context = browser.new_context(
                viewport={"width": 1400, "height": 900},
                locale="pt-PT"
            )

            page = context.new_page()

            for model_name, model_code, url in TESLA_URLS:
                print(f"A abrir {model_name}...", flush=True)

                page.goto(url, wait_until="domcontentloaded", timeout=60000)
                page.wait_for_timeout(20000)

                links = page.locator("a").evaluate_all(
                    """
                    els => els
                        .map(a => a.href)
                        .filter(h => h.includes('/order/'))
                    """
                )

                html = page.content()

                html_links = re.findall(
                    r'https://www\.tesla\.com/pt_PT/[a-z0-9]+/order/[^"\\s<]+',
                    html
                )

                links = list(set(links + html_links))

                print(f"{model_name}: encontrados {len(links)} carros", flush=True)

                for link in links:
                    clean_link = link.split("?")[0]
                    car_id = clean_link.split("/order/")[-1]

                    all_cars.append((model_name, model_code, car_id, clean_link))

            browser.close()

        print(f"TOTAL encontrados: {len(all_cars)}", flush=True)

        for model_name, model_code, car_id, clean_link in all_cars:
            if car_id not in seen:
                seen.add(car_id)
                save_seen(car_id)

                referral_link = f"{clean_link}?referral={REFERRAL}"

                msg = f"""
🚗 Novo Tesla encontrado!

Modelo: {model_name}

{referral_link}
"""

                print(msg, flush=True)
                send_telegram(msg)

        print("A aguardar 5 minutos...\n", flush=True)
        time.sleep(300)

    except Exception as e:
        print("Erro geral:", e, flush=True)
        time.sleep(60)
