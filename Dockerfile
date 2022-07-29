FROM python:3.9-slim-buster

WORKDIR "/app"

COPY requirements.txt .
COPY portal2mqtt.py .
COPY healthcheck.sh .

RUN pip install -r requirements.txt

HEALTHCHECK --start-period=30s --timeout=10s \
   CMD ./healthcheck.sh

CMD python3 portal2mqtt.py
