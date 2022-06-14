from smart_sauna_map.api import app


def test():
    rv = app.test_client().post(
        "/", json={
            "query": "新宿"
        }
    )
    print(rv)
