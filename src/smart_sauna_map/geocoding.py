# -*- coding: utf-8 -*-

from __future__ import annotations
import os
from os.path import join, dirname
from socket import timeout
import geopy
from dotenv import load_dotenv

load_dotenv(dotenv_path=join(dirname(__file__), ".env"))

GOOGLE_MAP_API_KEY = os.environ.get("GOOGLE_MAP_API_KEY")


def geocode(query: str, timeout: float = 30.0) -> dict[str, float | None]:
    # TODO: get_latlng.py と統合する
    status = {"ok": 200, "ng": 404}

    location = geopy.geocoders.GoogleV3(
        api_key=GOOGLE_MAP_API_KEY, domain="maps.google.co.jp", timeout=timeout
    ).geocode(query)
    if location:
        return {"lat": location.latitude, "lng": location.longitude}, status["ok"]
    return {"lat": None, "lng": None}, status["ng"]


if __name__ == "__main__":
    print(geocode("shinjuku"))
