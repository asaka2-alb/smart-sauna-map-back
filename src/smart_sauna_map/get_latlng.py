import argparse
import ast
from subprocess import PIPE, run
from typing import Dict
from urllib.parse import quote

import os
from os.path import join, dirname
from dotenv import load_dotenv

load_dotenv(dotenv_path=join(dirname(__file__), ".env"))

GOOGLE_MAP_API_KEY = os.environ.get("GOOGLE_MAP_API_KEY")


def main(query: str) -> Dict[str, float]:
    """Return a dict has "lat" and "lng" key."""
    default_latlng = {"lat": 35.6938253, "lng": 139.7033559}

    param = f"address\={quote(query)}\&region\=ja\&key\={GOOGLE_MAP_API_KEY}"
    url = f"https://maps.googleapis.com/maps/api/geocode/json\?{param}"
    cmd = f"curl {url}"
    res_byte = run(cmd, shell=True, stdout=PIPE, stderr=PIPE)
    res_dict = ast.literal_eval(res_byte.stdout.decode("utf-8"))

    if len(res_dict["results"]) != 1:
        return default_latlng

    return res_dict["results"][0]["geometry"]["location"]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("query", type=str)
    args = parser.parse_args()
    main(args.query)
