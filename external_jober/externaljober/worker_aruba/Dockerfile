


FROM python:3.9
WORKDIR /app
RUN apt-get update && \
    apt-get install -y zabbix-sender && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . ./
CMD ["python", "externaljober/worker_aruba/main.py"]





