from threading import Thread
from client import Bot
from app import app
import os

def start_web():
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
    )

Thread(target=start_web, daemon=True).start()

print("Bot Started 👍 Powered By @Faiz_Movies")
Bot().run()
