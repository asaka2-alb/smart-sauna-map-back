from smart_sauna_map.get_latlng import main
import pytest


class TestGetLagLng:

    @pytest.mark.parametrize(
        "query,expected", [
            ("新宿", {"lat": 35.6938253, "lng": 139.7033559}),
            ("池袋", {"lat": 35.7348314, "lng": 139.7077314}),
            ("押上", {"lat": 35.7113453, "lng": 139.8150661}),
        ],
    )
    def test_normal(self, query, expected):
        res = main(query)
        assert res == expected

    @pytest.mark.parametrize(
        "query,expected", [
            ("", {"lat": 35.6938253, "lng": 139.7033559}),
            ("存在しない地名xxx", {"lat": 35.6938253, "lng": 139.7033559}),
        ],
    )
    def test_abnormal(self, query, expected):
        res = main(query)
        assert res == expected
