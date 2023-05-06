# -*- coding: utf-8 -*-

from typing import Optional

from flask import Flask, abort, jsonify, make_response, request
from flask_cors import CORS  # type: ignore

from smart_sauna_map.geocoding import geocode as _geocode
from smart_sauna_map.search_sauna import search_sauna as _search_sauna
from smart_sauna_map.searcher.sauna_ikitai_searcher import SaunaIkitaiSearcher

app = Flask(__name__, static_folder="./build/static", template_folder="./build")
CORS(app)  # Cross Origin Resource Sharing


@app.route("/geocode", methods=["POST"])
def geocode():
    """Return coordinate refer to given keyword.

    Returns:
        Coordinate consists of latitude and longitude with JSON format.

    Examples:
        >>> python app.py
        >>> curl -X POST -H "Content-type: application/json"  -d '{"query": "御殿場"}'
            http://127.0.0.1:5000/geocode
        {"lat":35.3087683,"lng":138.9347872}
    """
    request_json: dict = request.get_json()
    query: Optional[str] = request_json.get("query", None)

    latlng = _geocode(query)
    if latlng["lat"] is None or latlng["lng"] is None:
        abort(404)

    return make_response(jsonify(latlng))


@app.route("/search_sauna", methods=["POST"])
def search_sauna():
    """Search sauna list.

    Returns:
        Hit saunas with JSON format.

    Examples:
        >>> python app.py
        >>> curl -X POST -H "Content-type: application/json" -d '{"keyword": "御殿場"}' http://127.0.0.1:5000/search_sauna
        [
            {"address":"xxxxx","ikitai":1045,"lat":35.2987346,"lng":138.9451729,"name":"xxxx"},
            {"address":"xxxxx","ikitai":688,"lat":35.3047105,"lng":138.9671482,"name":"xxxx"},
            ...,
        ]
    """

    keyword: str = request.get_json()["keyword"]
    searcher: str = (
        SaunaIkitaiSearcher()
        if "searcher" not in request.get_json()
        else eval(request.get_json()["searcher"] + "()")
    )
    sauna = _search_sauna(keyword=keyword, searcher=searcher)
    return make_response(jsonify(sauna))


@app.after_request
def after_request(response):
    response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
    response.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
    return response
