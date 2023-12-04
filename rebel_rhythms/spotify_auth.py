import webbrowser
from typing import Optional
import requests
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import os
from enum import Enum


class SpotifyScope(Enum):
    USER_READ_PRIVATE = "user-read-private"
    USER_READ_EMAIL = "user-read-email"
    USER_LIBRARY_READ = "user-library-read"
    USER_LIBRARY_MODIFY = "user-library-modify"
    PLAYLIST_READ_PRIVATE = "playlist-read-private"
    PLAYLIST_MODIFY_PRIVATE = "playlist-modify-private"
    PLAYLIST_MODIFY_PUBLIC = "playlist-modify-public"
    USER_READ_PLAYBACK_STATE = "user-read-playback-state"
    USER_MODIFY_PLAYBACK_STATE = "user-modify-playback-state"
    USER_READ_CURRENTLY_PLAYING = "user-read-currently-playing"
    USER_TOP_READ = "user-top-read"
    USER_FOLLOW_READ = "user-follow-read"
    USER_FOLLOW_MODIFY = "user-follow-modify"
    USER_READ_RECENTLY_PLAYED = "user-read-recently-played"
    UGC_IMAGE_UPLOAD = "ugc-image-upload"


class SpotifyAuth:
    class SimpleHandler(BaseHTTPRequestHandler):
        def __init__(self, *args, spotify_auth, **kwargs):
            self.spotify_auth = spotify_auth
            super().__init__(*args, **kwargs)

        def do_GET(self):
            if self.path.startswith("/callback"):
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                auth_code = self.path.split("=")[1]
                tokens = self.spotify_auth.get_access_token(auth_code)
                if tokens:
                    self.spotify_auth.store_tokens(tokens)

    def __init__(self, client_id, client_secret, redirect_uri, scope: Optional[list[SpotifyScope]] = None, tokens_file=None):
        if scope is None:
            scope = [s for s in SpotifyScope]
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.scope = " ".join([s.value for s in scope])
        if tokens_file is None:
            self.tokens_file = os.path.join(os.getcwd(), "tokens.json")
        else:
            self.tokens_file = tokens_file
        self.token_url = "https://accounts.spotify.com/api/token/"
        self.tokens = self.load_tokens()

    def initiate_authorization(self):
        webbrowser.open(self.get_authorization_url())
        self.run_server()
        self.tokens = self.load_tokens()

    def run_server(self):
        server = HTTPServer(
            ("localhost", 8080), lambda *args, **kwargs: self.SimpleHandler(*args, spotify_auth=self, **kwargs)
        )
        server.handle_request()

    def load_tokens(self):
        if os.path.exists(self.tokens_file):
            with open(self.tokens_file, "r") as file:
                return json.load(file)
        return None

    def store_tokens(self, tokens):
        with open(self.tokens_file, "w") as file:
            json.dump(tokens, file)

    def get_authorization_url(self):
        base_url = "https://accounts.spotify.com/authorize"
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
            "scope": self.scope,
        }
        return requests.get(base_url, params=params).url

    def get_access_token(self, auth_code):
        payload = {"grant_type": "authorization_code", "code": auth_code, "redirect_uri": self.redirect_uri}
        response = requests.post(self.token_url, data=payload, auth=(self.client_id, self.client_secret), headers=None)
        return response.json()

    def refresh_tokens(self):
        if not self.tokens or "refresh_token" not in self.tokens:
            raise ValueError("Tokens not found or refresh_token missing")

        refresh_token = self.tokens.get("refresh_token")
        payload = {"grant_type": "refresh_token", "refresh_token": refresh_token}
        response = requests.post(self.token_url, data=payload, auth=(self.client_id, self.client_secret), headers=None)
        return response.json()
