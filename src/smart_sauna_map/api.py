# -*- coding: utf-8 -*-

from typing import Optional

from flask import Flask, abort, jsonify, make_response, request
from flask_cors import CORS  # type: ignore

from smart_sauna_map.geocoding import geocode
from smart_sauna_map.search_sauna import search_sauna

app = Flask(__name__, static_folder="./build/static", template_folder="./build")
CORS(app)  # Cross Origin Resource Sharing


@app.route("/", methods=["GET", "POST"])
def index():
    request_json: dict = request.get_json()
    query: Optional[str] = request_json.get("query", None)

    latlng = geocode(query)
    if latlng["lat"] is None or latlng["lng"] is None:
        abort(404)

    return make_response(jsonify(latlng))


@app.route("/sauna", methods=["GET", "POST"])
def sauna():
    """Get sauna list.

    Returns:
        Response: Hit saunas.
    Example:
        >>> python src/smart_sauna_map/server.py
        >>> curl -X POST -H "Content-type: application/json"  -d '{"keyword": "御殿場",
            "prefecture": "shizuoka"}'  http://127.0.0.1:5000/sauna
    """
    keyword: str = request.get_json()["keyword"]
    prefecture: str = request.get_json()["prefecture"]
    sauna = search_sauna(keyword=keyword, prefecture=prefecture)
    return make_response(jsonify(sauna))


@app.after_request
def after_request(response):
    response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
    response.headers.add("Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS")
    return response


def echo_request(query):
    return [
        {"id": 0, "text": query},
    ]


def return_sample_response():
    return [
        {"id": 0, "text": "Hello, Smart Sauna Map!"},
    ]
