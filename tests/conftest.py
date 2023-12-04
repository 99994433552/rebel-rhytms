from dotenv import load_dotenv

load_dotenv(".env")
import pytest
from rebel_rhythms import SpotifyClient
import os


@pytest.fixture
def spotify_client():
    client_id = os.environ.get("SPOTIFY_CLIENT_ID")
    client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET")
    return SpotifyClient(client_id, client_secret)


@pytest.fixture
def user_id():
    return "spotify"


@pytest.fixture
def non_existent_user_id():
    return "https://open.spotify.com/user/vjwn3bbs03mv17fp9m5q00000?si=1b817dc948864e40"


@pytest.fixture
def album_id():
    return "6jbGBeBtwD05O0EV9RFjlC"


@pytest.fixture
def multiple_album_ids(album_id):
    return [album_id, "4XEccc9Poq5jJekD1FyVcY"]


@pytest.fixture
def non_existent_album_id():
    return "6jbGBeBtwD05O0EV9R0000"


@pytest.fixture
def artist_id():
    return "1ZwdS5xdxEREPySFridCfh"


@pytest.fixture
def multiple_artists_ids():
    return ["1ZwdS5xdxEREPySFridCfh", "4EnEZVjo3w1cwcQYePccay"]


@pytest.fixture
def non_existent_artist_id():
    return "6jbGBeBtwD05O0EV9R0000"


@pytest.fixture
def playlist_id():
    return "37i9dQZF1DWZtGWF9Ltb0N"


@pytest.fixture
def non_existent_playlist_id():
    return "6jbGBeBtwD05O0EV9R0000"


@pytest.fixture
def multiple_playlist_ids():
    return [
        "https://open.spotify.com/playlist/37i9dQZF1DWZtGWF9Ltb0N?si=2f50ea9500b345f1",
        "https://open.spotify.com/playlist/37i9dQZF1DWTv94Wk9KTkJ?si=73c5aafad94e447c",
    ]


@pytest.fixture
def track_uris():
    return (
        "spotify:track:4cCfprh4NrvyLGKN2rOCO7",
        "spotify:track:2oHt6KQZ5IXExcBEQhObjZ",
        "spotify:track:3At9iZJpHFkIsVFO4IKe4u",
        "spotify:track:1go8uqfAPRG3gQzpxHGFG1",
        "spotify:track:2yCz3n7e0rJXpALsmEs1JI",
    )


@pytest.fixture
def valid_track():
    return "07L2b1rNFcywc0coZYUzeV"


@pytest.fixture
def multiple_valid_tracks():
    return ["7tpzOkfjKlrs9XxPYrfjHx", "07L2b1rNFcywc0coZYUzeV"]


@pytest.fixture
def mixed_tracks(non_existent_track, valid_track):
    return [non_existent_track, valid_track]


@pytest.fixture
def non_existent_track():
    return "07L2b1rNFcywc0c0000000"
