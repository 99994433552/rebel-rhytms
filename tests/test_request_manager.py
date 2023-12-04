import pytest
from unittest.mock import MagicMock
from requests.exceptions import Timeout
from rebel_rhythms import SpotifyRequestManager, SpotifyClientException, UnauthorizedException


# Create a fixture for an instance of SpotifyRequestManager
@pytest.fixture
def spotify_manager(mocker):
    mock_auth = mocker.MagicMock()
    mock_market = "UA"
    return SpotifyRequestManager(mock_auth, mock_market)


# Mock the 'requests' library method
def mock_request(mocker, method, response_data, status_code=200):
    mock_response = MagicMock()
    mock_response.json.return_value = response_data
    mock_response.status_code = status_code
    mocker.patch(f"requests.{method}", return_value=mock_response)


# Test the _request method
def test_request_method(mocker, spotify_manager):
    mock_request(mocker, "get", {"data": "value"})
    result = spotify_manager._request("get", "/some/endpoint")
    assert result == {"data": "value"}


# Test timeout in _request method
def test_request_timeout(mocker, spotify_manager):
    mocker.patch("requests.get", side_effect=Timeout)
    with pytest.raises(SpotifyClientException):
        spotify_manager._request("get", "/some/endpoint")


# Test the get method
def test_get_method(mocker, spotify_manager):
    mock_request(mocker, "get", {"data": "value"})
    result = spotify_manager.get("/some/endpoint")
    assert result == {"data": "value"}


# Test the post method
def test_post_method(mocker, spotify_manager):
    mock_request(mocker, "post", {"data": "value"})
    result = spotify_manager.post("/some/endpoint")
    assert result == {"data": "value"}


# Test the put method
def test_put_method(mocker, spotify_manager):
    mock_request(mocker, "put", {"data": "value"})
    result = spotify_manager.put("/some/endpoint")
    assert result == {"data": "value"}


# Test the delete method
def test_delete_method(mocker, spotify_manager):
    mock_request(mocker, "delete", {"data": "value"})
    result = spotify_manager.delete("/some/endpoint")
    assert result == {"data": "value"}


# Test UnauthorizedException
def test_unauthorized_exception(mocker, spotify_manager):
    mock_request(mocker, "get", None, 401)

    # Mock the token refresh method to return True (indicating the token was refreshed successfully)
    mocker.patch.object(spotify_manager, "_refresh_token_if_required", return_value=True)

    with pytest.raises(UnauthorizedException):
        spotify_manager._request("get", "/some/endpoint")
