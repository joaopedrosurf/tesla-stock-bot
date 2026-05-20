import time
import requests
from bs4 import BeautifulSoup
from plyer import notification
import webbrowser

BOT_TOKEN = "TEU_TOKEN"
CHAT_ID = "TEU_CHAT_ID"

vistos = set()

modelos = {
    "Model 3": "https://www.tesla.com/pt_PT/inventory/new/m3?arrangeby=plh&zip=1000-000&range=0",
    "Model Y": "https://www.tesla.com/pt_PT/inventory/new/my?arrangeby=plh&zip=1000-000&range=0",
    "Model S": "https://www.tesla.com/pt_PT/inventory/new/ms?arrangeby=plh&zip=1000-000&range=0",
    "Model X": "https://www.tesla.com/pt_PT/inventory/new/mx?arrangeby=plh&zip=1000-000&range=0"
}

headers = {
    "User-Agent": "Mozilla/5.0"
}

def enviar_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": msg
    }
    requests.post(url, data=data)

print("BOT ARRANCOU NO MAC")
print("VINs já conhecidos:", len(vistos))

while True:
    total = 0

    for nome, url in modelos.items():
        try:
            print(f"A abrir {nome}...")

            resposta = requests.get(url, headers=headers)
            html = resposta.text

            soup = BeautifulSoup(html, "html.parser")

            links = soup.find_all("a")

            encontrados = 0

            for link in links:
                href = link.get("href")

                if href and "/order/" in href:

                    link_final = "https://www.tesla.com" + href.split("?")[0]

                    if link_final not in vistos:
                        vistos.add(link_final)

                        encontrados += 1
                        total += 1

                        mensagem = f"""🚗 Novo {nome} em inventário!

{link_final}
"""

                        print(mensagem)

                        enviar_telegram(mensagem)

                        notification.notify(
                            title=f"Novo {nome}",
                            message="Novo Tesla encontrado!",
                            timeout=5
                        )

                        webbrowser.open(link_final)

            print(f"{nome}: encontrados {encontrados} carros")

        except Exception as e:
            print("Erro:", e)

    print("TOTAL encontrados:", total)
    print("A aguardar 5 minutos...\n")

    time.sleep(300)
