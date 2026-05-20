from playwright.sync_api import sync_playwright
import requests
import time
import os
import re
from html import unescape

print("BOT ARRANCOU - VERSAO TESLA-INFO PLAYWRIGHT", flush=True)

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


def make_referral_link(link):
    link = unescape(link)
    link = link.split("?")[0]
    return f"{link}?referral={REFERRAL}"


seen = load_seen()
print(f"Carros já conhecidos: {len(seen)}", flush=True)


while True:
    try:
        print("A abrir Tesla-info com browser...", flush=True)

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
                TESLA_INFO_URL,
                wait_until="domcontentloaded",
                timeout=60000
            )

            page.wait_for_timeout(15000)

            html = page.content()

            hrefs = page.locator("a").evaluate_all(
                "els => els.map(a => a.href)"
            )

            browser.close()

        links = []

        for href in hrefs:
            if "tesla.com" in href and "/order/" in href:
                links.append(href)

        html_links = re.findall(
            r'https://www\.tesla\.com/pt_PT/[a-z0-9]+/order/[^"\s<]+',
            html
        )

        for link in html_links:
            links.append(link)

        links = list(set(links))

        print(f"Encontrados {len(links)} carros", flush=True)

        for link in links:
            car_id = link.split("/order/")[-1].split("?")[0]

            if car_id not in seen:
                seen.add(car_id)
                save_seen(car_id)

                referral_link = make_referral_link(link)

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
