FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY start_middleware.py /app/start_middleware.py
COPY config.template.yaml /app/config.template.yaml

CMD ["python", "/app/start_middleware.py"]