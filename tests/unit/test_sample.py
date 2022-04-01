import flask
from smart_sauna_map.__init__ import version  # type: ignore
from smart_sauna_map.server import return_sample_response


def test_check_version():
    expected_version = "0.1.0"
    assert version == expected_version


def test_check_flask_version():
    expected_version = "2.0.2"
    assert flask.__version__ == expected_version


def test_get_response_from_flask():
    # arrange: requestに含まれるパラメータ
    expected_res = [{"id": 0, "text": "Hello, Smart Sauna Map!"}]

    # act: requestを受けて呼ばれる関数を呼び出す
    res = return_sample_response()

    # assert: responseをチェック
    assert res == expected_res
