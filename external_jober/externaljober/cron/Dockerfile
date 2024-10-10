
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
COPY /opt/zabbix_custom/zabbix_WRK/external_jober /app
CMD ["python", "main.py"]



