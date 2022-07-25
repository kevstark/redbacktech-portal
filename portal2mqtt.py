#!/usr/bin/env python3

from wsgiref.util import request_uri
import paho.mqtt.client as mqtt
import json
import time
import pathlib
import bs4
import logging
import requests
from collections.abc import Mapping
import dotenv
import os

logger = logging.getLogger(__name__)
logging.basicConfig(
    filename=__name__,
    filemode='a',
    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
    datefmt='%H:%M:%S',
    level=logging.INFO
)

redbacktech_portal = {
    "site_url": "https://portal.redbacktech.com",
    "login_url": "/Account/Login",
    "request_url": {
        #"BannerInfo": "/api/v2/BannerInfo/",
        "BatteryWidget": "/api/v2/BatteryWidget/",
        "EnergyFlow": "/api/v2/EnergyFlow/",
        "History": "/api/v2/History/",
    },
}

def  mqtt_topic(id, endpoint, namespace="portal.redbacktech.com"):
    # portal.redbacktech.com/RB21101903120005/BannerInfo
    return f"{namespace}/{id}/{endpoint}"

def portal_mqtt_update(client, id, endpoint, data):
    topic = mqtt_topic(id, endpoint)
    logger.info(f"mqtt.publish: {topic} {json.dumps(data)}")
    client.publish(topic, json.dumps(data))

if __name__ == "__main__":
    config = {
        **dotenv.dotenv_values(".env.mqtt"),
        **dotenv.dotenv_values(".env.redbacktech"),
        **os.environ,  # override loaded values with environment variables
    }
    mqttc = mqtt.Client(config['MQTT_CLIENT'])
    mqttc.connect(config["MQTT_BROKER"], int(config["MQTT_PORT"]))

    login_url = redbacktech_portal["site_url"] + redbacktech_portal["login_url"]
    logger.info(f"Initialising portal session: {login_url}")
    s = requests.Session()
    g = s.get(login_url)
    logger.info(f"GET {g.status_code} {login_url}")
    g.raise_for_status()
    # Load the __RequestVerificationToken for replay
    token = bs4.BeautifulSoup(g.text, 'html.parser').find('input',{'name':'__RequestVerificationToken'})['value']
    logger.info(f"Session token: {token}")

    payload = { 'Email': config["REDBACKTECH_EMAIL"],
                'Password': config["REDBACKTECH_PASSWORD"],
                '__RequestVerificationToken': token }

    p = s.post(login_url, data=payload)
    logger.info(f"POST {p.status_code} {login_url}")
    p.raise_for_status()

    while True:
        for endpoint, uri in redbacktech_portal["request_url"].items():
            request_uri = redbacktech_portal["site_url"] + uri + config["REDBACKTECH_SYSID"]
            r = s.get(request_uri)
            logger.info(f"GET [{r.status_code}] {request_uri}")
            r.raise_for_status()

            data = json.loads(r.text)
            portal_mqtt_update(mqttc, config["REDBACKTECH_SYSID"], endpoint, data)

        time.sleep(int(config["REDBACKTECH_POLL"]))


