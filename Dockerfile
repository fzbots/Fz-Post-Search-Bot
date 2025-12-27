# Don't Remove Credit @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01

FROM python:3.10-slim

RUN apt update \
    && apt install -y git bash \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /VJ-Post-Search-Bot

COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["bash", "-c", "python3 app.py & python3 main.py"]
