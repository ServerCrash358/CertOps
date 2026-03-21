FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY certops/ ./certops/

WORKDIR /app/certops

CMD ["python", "main.py"]
