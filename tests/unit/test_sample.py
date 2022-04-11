import flask
from smart_sauna_map.__init__ import version  # type: ignore


def test_check_version():
    expected_version = "0.1.0"
    assert version == expected_version


def test_check_flask_version():
    expected_version = "2.0.2"
    assert flask.__version__ == expected_version
