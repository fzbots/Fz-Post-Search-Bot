# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'FaizMovies'


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7860)
