#Obtener la versión de python e imagen desde la siguiente URL -> https://hub.docker.com/_python
FROM python:3.10-slim

RUN apt-get update -y

COPY . /app
WORKDIR /app

RUN pip install --no-cache-dir -r requirements.txt
ENTRYPOINT ["python"]
CMD ["app.py"]