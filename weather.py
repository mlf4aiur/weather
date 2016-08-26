#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging
import os
from urllib.parse import urlencode
from urllib import request

from flask import Flask, jsonify

__version__ = '0.9.0'

app = Flask(__name__)

PORT = int(os.environ.get("PORT", 5000))
APP_ID = os.environ.get("APP_ID")
TEMP_SCALE = os.environ.get("TEMP_SCALE", "C")
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")


def is_metric():
    return False if TEMP_SCALE == "F" else True


def get_request(url, values=None):
    headers = {"User-Agent": "Python urllib2",
               "Content-Type": "application/json"}
    if values:
        data = urlencode(values)
        full_url = "{url}?{data}".format(url=url, data=data)
    else:
        full_url = url
    app.logger.debug("Full URL is: {full_url}".format(full_url=full_url))
    _request = request.Request(full_url, headers=headers)
    try:
        response = request.urlopen(_request)
        result = response.read()
        response.close()
        return result
    except Exception as error:
        app.logger.exception(error)


def lookup_weather(city):
    url = "http://api.openweathermap.org/data/2.5/weather"
    unit = "metric" if is_metric() else "imperial"
    values = dict(q=city, units=unit, APPID=APP_ID)
    return get_request(url, values)


def convert_to_dict(response):
    output_format = "Celsius" if is_metric() else "Farenheit"
    output = json.loads(response)
    result = dict(
        city=output["name"],
        country=output["sys"]["country"],
        temp=output["main"]["temp"],
        format=output_format)
    return result


@app.route("/")
def index():
    return "/weather/&lt;city&gt;"


@app.route("/healthz")
def health():
    return "ok"


@app.route("/weather/<city>")
def weather(city):
    response = lookup_weather(city)
    if response:
        app.logger.info("Response from external API is: {response}".format(
            response=response))
        result = convert_to_dict(response.decode())
        result["success"] = True
        return jsonify(result)
    else:
        return jsonify(success=False)


if __name__ == "__main__":
    formatter = logging.Formatter(
        "%(asctime)s | %(pathname)s:%(lineno)d | "
        "%(funcName)s | %(levelname)s | %(message)s ")
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.getLevelName(LOG_LEVEL))
    app.run(host="0.0.0.0", port=PORT)
