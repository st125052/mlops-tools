FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY middleware.py /app/middleware.py
COPY config.template.yaml /app/config.template.yaml

CMD ["python", "/app/middleware.py"]