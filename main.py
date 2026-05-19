import requests
import time

while True:
    try:
        url = "https://query1.finance.yahoo.com/v8/finance/chart/TSLA"

        response = requests.get(url)

        data = response.json()

        price = data["chart"]["result"][0]["meta"]["regularMarketPrice"]

        print(f"Tesla stock price: ${price}")

    except Exception as e:
        print("Error:", e)

    time.sleep(60)
