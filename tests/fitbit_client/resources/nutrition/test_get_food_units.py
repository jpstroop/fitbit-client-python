# tests/fitbit_client/resources/nutrition/test_get_food_units.py

"""Tests for the get_food_units endpoint."""


def test_get_food_units_success(nutrition_resource, mock_response):
    """Test successful retrieval of food units"""
    mock_response.json.return_value = [
        {"id": 147, "name": "gram", "plural": "grams"},
        {"id": 204, "name": "medium", "plural": "mediums"},
    ]
    nutrition_resource.oauth.request.return_value = mock_response
    result = nutrition_resource.get_food_units()
    assert result == mock_response.json.return_value
    nutrition_resource.oauth.request.assert_called_once_with(
        "GET",
        "https://api.fitbit.com/1/foods/units.json",
        data=None,
        json=None,
        params=None,
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )
