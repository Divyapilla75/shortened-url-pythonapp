FROM python:3.10

WORKDIR /app

COPY requirements.txt requirements.txt

RUN mkdir -p /data
RUN chmod 777 /data

RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "app.py"]
