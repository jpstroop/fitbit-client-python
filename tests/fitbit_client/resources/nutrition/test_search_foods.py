# tests/fitbit_client/resources/nutrition/test_search_foods.py

"""Tests for the search_foods endpoint."""


def test_search_foods_success(nutrition_resource, mock_response_factory):
    """Test successful food search"""
    mock_response = mock_response_factory(
        200,
        {"foods": [{"foodId": 12345, "name": "Test Food", "brand": "Test Brand", "calories": 100}]},
    )
    nutrition_resource.oauth.request.return_value = mock_response
    result = nutrition_resource.search_foods(query="test food")
    assert result == mock_response.json.return_value
    nutrition_resource.oauth.request.assert_called_once_with(
        "GET",
        "https://api.fitbit.com/1/foods/search.json",
        data=None,
        json=None,
        params={"query": "test food"},
        headers={"Accept-Locale": "en_US", "Accept-Language": "en_US"},
    )
