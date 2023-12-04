from rebel_rhythms import SpotifyClient, SimplifiedAlbumObject, ArtistObject, Track, SimplifiedPlaylistObject
import pytest
from typing import Generator


class TestSearch:
    @pytest.mark.parametrize(
        "query, search_type, max_items, expected_instance_type",
        [
            ("Distorted Heights-Painkiller", "track", 1, Track),
            ("Distorted Heights Diesel Soul", "album", 2, SimplifiedAlbumObject),
            ("Distorted Heights", "artist", 1, ArtistObject),
            ("Sub Low", "playlist", 1, SimplifiedPlaylistObject),
            ("Scorn Gyral", "album", None, SimplifiedAlbumObject),
        ],
    )
    def test_search(
        self, spotify_client: SpotifyClient, query: str, search_type: str, max_items: int, expected_instance_type
    ):
        if max_items is None:
            items = spotify_client.search(query, search_type=search_type)
        else:
            items = spotify_client.search(query, search_type=search_type, max_items=max_items)
        assert isinstance(items, Generator)
        assert all(isinstance(item, expected_instance_type) for item in items)

    def test_invalid_search_type(self, spotify_client: SpotifyClient):
        with pytest.raises(ValueError):
            spotify_client.search(query="test", search_type="invalid_type")

    def test_dict_query(self, spotify_client: SpotifyClient):
        query_dict = {"label": "Position Chrome"}
        result = spotify_client.search(query=query_dict, search_type="album")
        assert isinstance(result, Generator)
        assert len(list(result)) == 64
        assert all(isinstance(item, SimplifiedAlbumObject) for item in result)
