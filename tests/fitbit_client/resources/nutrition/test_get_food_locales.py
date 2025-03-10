# tests/fitbit_client/resources/nutrition/test_get_food_locales.py

"""Tests for the get_food_locales endpoint."""


def test_get_food_locales_success(nutrition_resource, mock_response_factory):
    """Test successful retrieval of food locales"""
    mock_response = mock_response_factory(
        200,
        [
            {"value": "en_US", "label": "United States"},
            {"value": "en_GB", "label": "United Kingdom"},
        ],
    )
    nutrition_resource.oauth.request.return_value = mock_response
    result = nutrition_resource.get_food_locales()
    assert result == mock_response.json.return_value
    nutrition_resource.oauth.request.assert_called_once_with(
        "GET",
        "https://api.fitbit.com/1/foods/locales.json",
        data=None,
        json=None,
        params=None,
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )
