import argparse
import ast
import os
from os.path import dirname, join
from subprocess import PIPE, run
from typing import Dict
from urllib.parse import quote

from dotenv import load_dotenv

load_dotenv(dotenv_path=join(dirname(__file__), ".env"))

GOOGLE_MAP_API_KEY = os.environ.get("GOOGLE_MAP_API_KEY")


def get_lat_lng(query: str):
    # TODO: geocode.py と統合する
    param = f"address\={quote(query)}\&region\=ja\&key\={GOOGLE_MAP_API_KEY}"
    url = f"https://maps.googleapis.com/maps/api/geocode/json\?{param}"
    cmd = f"curl {url}"
    res = run(cmd, shell=True, stdout=PIPE, stderr=PIPE)
    return ast.literal_eval(res.stdout.decode("utf-8"))


def main(query: str) -> Dict[str, float]:
    """Return a dict has "lat" and "lng" key."""
    default_latlng = {"lat": None, "lng": None}
    res = get_lat_lng(query)
    # TODO: We will remove this block, if an appropriate error handling will be implemented.
    if len(res["results"]) != 1:
        return default_latlng, 404

    return res["results"][0]["geometry"]["location"], 200


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("query", type=str)
    args = parser.parse_args()
    main(args.query)
