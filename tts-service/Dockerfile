FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y espeak libespeak-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

RUN mkdir -p /app/audio

EXPOSE 8004

CMD ["python", "app.py"]
