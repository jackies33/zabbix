


FROM python:3.9
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . ./
RUN mkdir -p /tmp
CMD ["python", "externaljober/worker_aruba/main.py"]





