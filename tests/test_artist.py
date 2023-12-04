import pytest
from rebel_rhythms import spotify_client, ArtistObject, ResourceNotFoundException, IncludeGroups, BrowseCategory
from typing import List

from rebel_rhythms.models import SimplifiedAlbumObject


class TestArtist:
    def test_get_artist(self, spotify_client: spotify_client.SpotifyClient, artist_id: str):
        artist = spotify_client.get_artist(artist_id)
        assert isinstance(artist, ArtistObject)
        assert artist.id == artist_id

    def test_get_non_existing_artist(self, spotify_client: spotify_client.SpotifyClient, non_existent_artist_id: str):
        with pytest.raises(ResourceNotFoundException):
            spotify_client.get_artist(non_existent_artist_id)

    def test_get_multiple_artists(self, spotify_client: spotify_client.SpotifyClient, multiple_artists_ids: List[str]):
        artists = spotify_client.get_artists(multiple_artists_ids)
        assert len(artists) == len(multiple_artists_ids)
        assert all([isinstance(artist, ArtistObject) for artist in artists])

    def test_get_multiple_artists_with_non_existing_artist(
        self,
        spotify_client: spotify_client.SpotifyClient,
        multiple_artists_ids: List[str],
        non_existent_artist_id: str,
    ):
        multiple_artists_ids.append(non_existent_artist_id)
        assert len(spotify_client.get_artists(multiple_artists_ids)) == 2

    def test_get_non_existing_multiple_artists(
        self, spotify_client: spotify_client.SpotifyClient, non_existent_artist_id: str
    ):
        assert not spotify_client.get_artists(non_existent_artist_id)

    def test_get_multiple_same_artists(self, spotify_client: spotify_client.SpotifyClient, artist_id: str):
        assert len(spotify_client.get_artists([artist_id, artist_id])) == 2

    def test_get_artists_with_exceeding_limit(self, spotify_client: spotify_client.SpotifyClient, artist_id: str):
        with pytest.raises(ValueError):
            spotify_client.get_artists([artist_id] * 51)

    def test_get_artists_max_limit(self, spotify_client: spotify_client.SpotifyClient, artist_id: str):
        assert len(spotify_client.get_artists([artist_id] * 50)) == 50

    def test_get_artist_albums(self, spotify_client: spotify_client.SpotifyClient):
        artist_id = "https://open.spotify.com/artist/3CHcm8D4vuXQOghEx5BstB?si=YNIBW2t_Qh23sa2juTWQZQ"
        albums = spotify_client.get_artist_albums(artist_id)
        assert len(list(albums)) == 2

    @pytest.mark.parametrize(
        "include_groups",
        [
            None,
            [IncludeGroups.ALBUM],
            [IncludeGroups.SINGLE],
            [IncludeGroups.APPEARS_ON],
            [IncludeGroups.COMPILATION],
            [IncludeGroups.ALBUM, IncludeGroups.SINGLE],
            [IncludeGroups.ALBUM, IncludeGroups.SINGLE, IncludeGroups.APPEARS_ON, IncludeGroups.COMPILATION],
        ],
    )
    def test_get_artist_albums(self, spotify_client, artist_id, include_groups: List[IncludeGroups]):
        result = list(spotify_client.get_artist_albums(artist_id, include_groups, max_items=4))
        assert len(result) == 4
        assert all(isinstance(album, SimplifiedAlbumObject) for album in result)

    def test_get_artist_albums_with_invalid_include_group(self, spotify_client, artist_id):
        with pytest.raises(TypeError):
            spotify_client.get_artist_albums(artist_id, include_groups=["NotAnEnumInstance"])

    def test_get_artist_top_tracks(self, spotify_client: spotify_client.SpotifyClient, artist_id: str):
        top_tracks = spotify_client.get_artist_top_tracks(artist_id)
        assert len(top_tracks) == 10

    def test_get_non_existence_artist_top_tracks(
        self, spotify_client: spotify_client.SpotifyClient, non_existent_artist_id: str
    ):
        with pytest.raises(ResourceNotFoundException):
            spotify_client.get_artist_top_tracks(non_existent_artist_id)

    def test_get_artist_related_artists(self, spotify_client: spotify_client.SpotifyClient, artist_id: str):
        related_artists = spotify_client.get_related_artists(artist_id)
        assert len(related_artists) == 20
        assert all(isinstance(artist, ArtistObject) for artist in related_artists)

    def test_get_non_existence_artist_related_artists(
        self, spotify_client: spotify_client.SpotifyClient, non_existent_artist_id: str
    ):
        with pytest.raises(ResourceNotFoundException):
            spotify_client.get_related_artists(non_existent_artist_id)
