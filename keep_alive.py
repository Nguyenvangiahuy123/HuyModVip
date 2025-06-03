from flask import Flask
import threading
import requests
import time

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    # Chạy Flask web server trong thread riêng
    threading.Thread(target=run).start()

    # Tự ping web server giữ bot sống
    while True:
        try:
            requests.get("http://localhost:8080")
            print("Ping success")
        except Exception as e:
            print(f"Ping failed: {e}")
        time.sleep(300)  # 5 phút ping 1 lần
