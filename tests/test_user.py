from rebel_rhythms import SpotifyClient, CurrentUser, ItemsType, ArtistObject, Track, User, SpotifyClientException
import pytest


class TestUser:
    def test_get_current_user_profile(self, spotify_client: SpotifyClient):
        profile = spotify_client.get_current_user_profile()
        assert profile is not None
        assert isinstance(profile, CurrentUser)

    @pytest.mark.parametrize(
        "items_type",
        [ItemsType.ARTISTS, ItemsType.TRACKS],
    )
    def test_get_user_top_items(self, spotify_client: SpotifyClient, items_type: ItemsType):
        top_items = spotify_client.get_user_top_items(items_type=items_type)
        if items_type == ItemsType.ARTISTS:
            assert all(isinstance(item, ArtistObject) for item in top_items)
        else:
            assert all(isinstance(item, Track) for item in top_items)

    @pytest.mark.parametrize(
        "items_type,time_range",
        [(ItemsType.ARTISTS, "long_term"), (ItemsType.TRACKS, "medium_term")],
    )
    def test_get_user_top_items_with_time_range(
        self, spotify_client: SpotifyClient, items_type: ItemsType, time_range: str
    ):
        top_items = spotify_client.get_user_top_items(items_type=items_type, time_range=time_range)
        if items_type == ItemsType.ARTISTS:
            assert all(isinstance(item, ArtistObject) for item in top_items)
        else:
            assert all(isinstance(item, Track) for item in top_items)

    def test_get_user_top_items_invalid_type(self, spotify_client: SpotifyClient):
        with pytest.raises(ValueError):
            spotify_client.get_user_top_items(items_type="invalid_type")

    def test_get_user_top_items_invalid_time_range(self, spotify_client: SpotifyClient):
        with pytest.raises(ValueError):
            spotify_client.get_user_top_items(items_type=ItemsType.ARTISTS, time_range="invalid_time_range")

    def test_get_limited_user_top_items(self, spotify_client: SpotifyClient):
        top_items = list(spotify_client.get_user_top_items(items_type=ItemsType.ARTISTS, max_items=10))
        assert len(top_items) == 10
        assert all(isinstance(item, ArtistObject) for item in top_items)

    def test_get_user_profile(self, spotify_client: SpotifyClient, user_id: str):
        profile = spotify_client.get_user_profile(user_id=user_id)
        assert isinstance(profile, User)

    def test_get_user_profile_invalid_id(self, spotify_client: SpotifyClient, non_existent_user_id: str):
        with pytest.raises(SpotifyClientException):
            spotify_client.get_user_profile(user_id=non_existent_user_id)

    def test_follow_playlist(self, spotify_client: SpotifyClient, playlist_id: str):
        response = spotify_client.follow_playlist(playlist_id)
        assert response is None
        user_playlists = spotify_client.get_current_user_playlists()
        assert any(playlist.id == playlist_id for playlist in user_playlists)

    def test_follow_playlist_invalid_id(self, spotify_client: SpotifyClient, non_existent_playlist_id: str):
        with pytest.raises(SpotifyClientException):
            spotify_client.follow_playlist(non_existent_playlist_id)

    def test_unfollow_playlist(self, spotify_client: SpotifyClient, playlist_id: str):
        response = spotify_client.follow_playlist(playlist_id)
        assert response is None
        response = spotify_client.unfollow_playlist(playlist_id)
        assert response is None
        user_playlists = spotify_client.get_current_user_playlists()
        assert not any(playlist.id == playlist_id for playlist in user_playlists)
