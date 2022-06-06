from smart_sauna_map.get_latlng import main
import pytest


mock_res = {
    'error_message': "Invalid request. Missing the 'address', 'components', 'latlng' or 'place_id' parameter.",
    'results': [], 'status': 'INVALID_REQUEST'
}


class TestGetLagLng:

    @pytest.mark.parametrize(
        "query,expected", [
            ("新宿", ({"lat": 35.6938253, "lng": 139.7033559}, 200)),
            ("池袋", ({"lat": 35.7348314, "lng": 139.7077314}, 200)),
            ("押上", ({"lat": 35.7113453, "lng": 139.8150661}, 200)),
        ],
    )
    def test_normal(self, query, expected):
        res = main(query)
        assert res == expected

    @pytest.mark.parametrize(
        "query,expected", [
            ("", ({"lat": None, "lng": None}, 404)),
            ("存在しない地名xxx", ({"lat": None, "lng": None}, 404)),
        ],
    )
    def test_abnormal(self, mocker, query, expected):
        mocker.patch(
            "smart_sauna_map.get_latlng.get_lat_lng", return_value=mock_res
        )
        res = main(query)
        assert res == expected
