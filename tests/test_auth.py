import json
from unittest.mock import mock_open, patch, Mock, call
from rebel_rhythms import SpotifyAuth


class TestSpotifyAuth:
    def test_initiate_authorization(self):
        with patch("webbrowser.open") as mock_webbrowser, patch.object(SpotifyAuth, "run_server") as mock_run_server:
            auth = SpotifyAuth("client_id", "client_secret", "http://localhost:8080/callback")
            auth.initiate_authorization()

            mock_webbrowser.assert_called_once()
            mock_run_server.assert_called_once()

    def test_load_tokens_existing_file(self):
        with patch("os.path.exists", return_value=True), patch(
            "builtins.open", mock_open(read_data=json.dumps({"access_token": "some_token"}))
        ):
            auth = SpotifyAuth("client_id", "client_secret", "http://localhost:8080/callback")
            tokens = auth.load_tokens()

            assert tokens == {"access_token": "some_token"}

    def test_load_tokens_missing_file(self):
        with patch("os.path.exists", return_value=False):
            auth = SpotifyAuth("client_id", "client_secret", "http://localhost:8080/callback")
            tokens = auth.load_tokens()

            assert tokens is None

    def test_store_tokens(self):
        with patch("builtins.open", mock_open(read_data=json.dumps({"key": "value"}))) as mock_file:
            auth = SpotifyAuth("client_id", "client_secret", "http://localhost:8080/callback")
            auth.store_tokens({"access_token": "some_token"})

            calls = [call("{"), call('"access_token"'), call(": "), call('"some_token"'), call("}")]
            mock_file().write.assert_has_calls(calls)

    def test_get_authorization_url(self):
        with patch("requests.get") as mock_get:
            mock_get.return_value.url = "some_url"

            auth = SpotifyAuth("client_id", "client_secret", "http://localhost:8080/callback")
            url = auth.get_authorization_url()

            assert url == "some_url"

    def test_get_access_token(self):
        with patch("requests.post") as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {"access_token": "some_token"}
            mock_post.return_value = mock_response

            auth = SpotifyAuth("client_id", "client_secret", "http://localhost:8080/callback")
            tokens = auth.get_access_token("auth_code")

            assert tokens == {"access_token": "some_token"}

    def test_refresh_tokens(self):
        with patch("requests.post") as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {"access_token": "new_token"}
            mock_post.return_value = mock_response

            auth = SpotifyAuth("client_id", "client_secret", "http://localhost:8080/callback")
            auth.tokens = {"refresh_token": "some_refresh_token"}

            new_tokens = auth.refresh_tokens()

            assert new_tokens == {"access_token": "new_token"}
