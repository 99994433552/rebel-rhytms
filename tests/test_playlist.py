from rebel_rhythms import (
    SpotifyClient,
    Playlist,
    ResourceNotFoundException,
    PlaylistTrackObject,
    SimplifiedPlaylistObject,
    ImageObject,
)
import pytest
import time
from typing import Generator, Tuple
from rebel_rhythms.custom_exceptions import BadRequestException, ForbiddenException


@pytest.fixture
def new_playlist(spotify_client: SpotifyClient) -> Playlist:
    playlist = spotify_client.create_playlist("Test Playlist")
    yield playlist
    spotify_client.unfollow_playlist(playlist.id)


@pytest.fixture
def user_id():
    return "https://open.spotify.com/user/rinsefm?si=6265129abebc40fd"


@pytest.fixture
def non_existent_user_id():
    return "https://open.spotify.com/user/rinsefmxxxx"


@pytest.fixture
def playlist_with_tracks(spotify_client: SpotifyClient, track_uris: Tuple[str, ...]):
    playlist = spotify_client.create_playlist("Test Playlist")
    spotify_client.add_tracks_to_playlist(playlist.id, track_uris)
    yield playlist.id


@pytest.fixture
def playlist_cover_image():
    return "tests/content/test_cover.jpeg"


@pytest.fixture
def invalid_playlist_cover_image():
    return "tests/content/oversized_image.jpg"


@pytest.fixture
def non_existent_playlist_cover_image():
    return "tests/content/non_existent_image.jpg"


class TestPlaylist:
    def test_get_playlist(self, spotify_client: SpotifyClient, playlist_id: str):
        playlist = spotify_client.get_playlist(playlist_id)
        assert isinstance(playlist, Playlist)
        assert playlist.id == playlist_id

    def test_get_non_existing_playlist(self, spotify_client: SpotifyClient, non_existent_playlist_id: str):
        with pytest.raises(ResourceNotFoundException):
            spotify_client.get_playlist(non_existent_playlist_id)

    def test_create_playlist_default(self, spotify_client: SpotifyClient):
        playlist = spotify_client.create_playlist("My New Playlist")
        assert isinstance(playlist, Playlist)
        assert playlist.public == True
        assert playlist.collaborative == False
        assert playlist.name == "My New Playlist"
        assert playlist.description == None
        assert playlist.tracks.items == []

    def test_create_private_playlist(self, spotify_client: SpotifyClient):
        playlist = spotify_client.create_playlist("My New Playlist", public=False)
        assert isinstance(playlist, Playlist)
        assert playlist.public == False
        assert playlist.collaborative == False
        assert playlist.name == "My New Playlist"
        assert playlist.description == None
        assert playlist.tracks.items == []

    def test_create_collaborative_playlist(self, spotify_client: SpotifyClient):
        playlist = spotify_client.create_playlist("My New Playlist", public=False, collaborative=True)
        assert isinstance(playlist, Playlist)
        assert playlist.public == False
        assert playlist.collaborative == True

    def test_create_collaborative_and_public_playlist(self, spotify_client: SpotifyClient):
        with pytest.raises(ValueError, match="You can't set both 'public' and 'collaborative' to True."):
            spotify_client.create_playlist("Invalid Playlist", public=True, collaborative=True)

    def test_invalid_public_param(self, spotify_client: SpotifyClient):
        with pytest.raises(ValueError, match="The 'public' parameter must be a boolean."):
            spotify_client.create_playlist("Invalid Playlist", public="not_a_bool")

    def test_invalid_collaborative_param(self, spotify_client: SpotifyClient):
        with pytest.raises(ValueError, match="The 'collaborative' parameter must be a boolean."):
            spotify_client.create_playlist("Invalid Playlist", collaborative="not_a_bool")

    def test_change_playlist_name(self, spotify_client: SpotifyClient):
        playlist = spotify_client.create_playlist("Initial Playlist Name")
        spotify_client.change_playlist_details(playlist.id, name="New Playlist Name")

        updated_playlist = spotify_client.get_playlist(playlist.id)
        assert updated_playlist.name == "New Playlist Name"

    def test_change_playlist_description(self, spotify_client: SpotifyClient):
        playlist = spotify_client.create_playlist("Playlist with Description", description="Initial Description")
        time.sleep(2)
        spotify_client.change_playlist_details(playlist.id, description="New Description")

        updated_playlist = spotify_client.get_playlist(playlist.id)
        assert updated_playlist.description == "New Description"

    def test_change_playlist_to_private(self, spotify_client: SpotifyClient):
        playlist = spotify_client.create_playlist("Public Playlist")
        spotify_client.change_playlist_details(playlist.id, public=False)

        updated_playlist = spotify_client.get_playlist(playlist.id)
        assert updated_playlist.public == False

    def test_make_playlist_collaborative(self, spotify_client: SpotifyClient):
        playlist = spotify_client.create_playlist("Non-Collaborative Playlist", public=False)
        spotify_client.change_playlist_details(playlist.id, collaborative=True)

        updated_playlist = spotify_client.get_playlist(playlist.id)
        assert updated_playlist.collaborative == True

    def test_change_multiple_details(self, spotify_client: SpotifyClient):
        playlist = spotify_client.create_playlist("Old Playlist", description="Old Description")
        time.sleep(2)
        spotify_client.change_playlist_details(playlist.id, name="New Playlist", description="New Description")

        updated_playlist = spotify_client.get_playlist(playlist.id)
        assert updated_playlist.name == "New Playlist"
        assert updated_playlist.description == "New Description"

    def test_invalid_public_param(self, spotify_client: SpotifyClient):
        playlist = spotify_client.create_playlist("Test Playlist")
        with pytest.raises(ValueError, match="The 'public' parameter must be a boolean."):
            spotify_client.change_playlist_details(playlist.id, public="not_a_bool")

    def test_invalid_collaborative_param(self, spotify_client: SpotifyClient):
        playlist = spotify_client.create_playlist("Test Playlist", public=False)
        with pytest.raises(ValueError, match="The 'collaborative' parameter must be a boolean."):
            spotify_client.change_playlist_details(playlist.id, collaborative="not_a_bool")

    def test_invalid_collaborative_and_public_combo(self, spotify_client: SpotifyClient):
        playlist = spotify_client.create_playlist("Test Playlist")
        with pytest.raises(ValueError, match="You can't set both 'public' and 'collaborative' to True."):
            spotify_client.change_playlist_details(playlist.id, public=True, collaborative=True)

    def test_get_all_playlist_tracks(self, spotify_client: SpotifyClient, playlist_id: str):
        track_gen = spotify_client.get_all_playlist_tracks(playlist_id)
        assert isinstance(track_gen, Generator)

        tracks = list(track_gen)
        assert len(tracks) >= 3
        for track in tracks:
            assert isinstance(track, PlaylistTrackObject)

    def test_get_limited_playlist_tracks(self, spotify_client: SpotifyClient, playlist_id: str):
        track_gen = spotify_client.get_all_playlist_tracks(playlist_id, max_items=2)
        assert isinstance(track_gen, Generator)

        tracks = list(track_gen)
        assert len(tracks) == 2
        for track in tracks:
            assert isinstance(track, PlaylistTrackObject)

    def test_get_zero_playlist_tracks(self, spotify_client: SpotifyClient, playlist_id: str):
        track_gen = spotify_client.get_all_playlist_tracks(playlist_id, max_items=0)
        assert isinstance(track_gen, Generator)

        tracks = list(track_gen)
        assert len(tracks) == 0

    def test_get_playlist_tracks_nonexistent_playlist(
        self, spotify_client: SpotifyClient, non_existent_playlist_id: str
    ):
        with pytest.raises(ResourceNotFoundException):
            list(spotify_client.get_all_playlist_tracks(non_existent_playlist_id))

    def test_add_single_track_to_playlist(
        self, spotify_client: SpotifyClient, new_playlist: Playlist, track_uris: Tuple[str, ...]
    ):
        playlist_id = new_playlist.id
        track = track_uris[0]
        response = spotify_client.add_tracks_to_playlist(playlist_id, track_uris[0])
        assert "snapshot_id" in response

        tracks = list(spotify_client.get_all_playlist_tracks(playlist_id))
        assert len(tracks) == 1

    def test_add_multiple_tracks_to_playlist(
        self, spotify_client: SpotifyClient, new_playlist: Playlist, track_uris: Tuple[str, ...]
    ):
        playlist_id = new_playlist.id

        response = spotify_client.add_tracks_to_playlist(playlist_id, track_uris)
        assert "snapshot_id" in response

        tracks = list(spotify_client.get_all_playlist_tracks(playlist_id))
        assert set(track.track.uri for track in tracks) == set(track_uris)

    def test_add_tracks_invalid_uris(self, spotify_client: SpotifyClient, new_playlist: Playlist):
        playlist_id = new_playlist.id
        invalid_uris = ["invalid_uri_1", "invalid_uri_2"]

        with pytest.raises(ValueError):
            spotify_client.add_tracks_to_playlist(playlist_id, invalid_uris)

    def test_add_tracks_to_nonexistent_playlist(
        self, spotify_client: SpotifyClient, track_uris: Tuple[str], non_existent_playlist_id: str
    ):
        with pytest.raises(ResourceNotFoundException):
            spotify_client.add_tracks_to_playlist(non_existent_playlist_id, track_uris)

    def test_add_tracks_empty_playlist_id(self, spotify_client: SpotifyClient, track_uris: Tuple[str]):
        with pytest.raises(ValueError):
            spotify_client.add_tracks_to_playlist("", track_uris)

    def test_add_tracks_empty_uri_list(self, spotify_client: SpotifyClient, new_playlist: Playlist):
        with pytest.raises(BadRequestException):
            spotify_client.add_tracks_to_playlist(new_playlist.id, [])

    def test_add_tracks_negative_position(
        self, spotify_client: SpotifyClient, new_playlist: Playlist, track_uris: Tuple[str]
    ):
        with pytest.raises(ValueError):
            spotify_client.add_tracks_to_playlist(new_playlist.id, track_uris, position=-1)

    def test_add_tracks_large_position(
        self, spotify_client: SpotifyClient, new_playlist: Playlist, track_uris: Tuple[str]
    ):
        with pytest.raises(ForbiddenException):
            spotify_client.add_tracks_to_playlist(new_playlist.id, track_uris, position=9999)

    def test_add_tracks_uri_list_upper_limit(
        self, spotify_client: SpotifyClient, new_playlist: Playlist, track_uris: Tuple[str]
    ):
        large_track_uris = [track_uris[0]] * 100
        response = spotify_client.add_tracks_to_playlist(new_playlist.id, large_track_uris)
        assert "snapshot_id" in response

    def test_remove_single_track(self, spotify_client: SpotifyClient, new_playlist, track_uris):
        spotify_client.add_tracks_to_playlist(new_playlist.id, [track_uris[0]])
        response = spotify_client.remove_playlist_items(new_playlist.id, track_uris[0])
        assert "snapshot_id" in response
        actual_track_list = list(spotify_client.get_all_playlist_tracks(new_playlist.id))
        assert track_uris[0] not in [track.track.uri for track in actual_track_list]

    def test_remove_multiple_tracks(self, spotify_client: SpotifyClient, playlist_with_tracks, track_uris):
        response = spotify_client.remove_playlist_items(playlist_with_tracks, track_uris[:3])

        assert "snapshot_id" in response
        actual_track_list = list(spotify_client.get_all_playlist_tracks(playlist_with_tracks))
        assert set(track_uris[:3]) & set([track.track.uri for track in actual_track_list]) == set()

    def test_remove_nonexistent_tracks(self, spotify_client: SpotifyClient, playlist_with_tracks):
        assert "snapshot_id" in spotify_client.remove_playlist_items(
            playlist_with_tracks, "spotify:track:4cCfprh4NrvyLGKN2r0000"
        )

    def test_remove_from_nonexistent_playlist(
        self, spotify_client: SpotifyClient, track_uris, non_existent_playlist_id
    ):
        with pytest.raises(ResourceNotFoundException):
            spotify_client.remove_playlist_items(non_existent_playlist_id, track_uris)

    def test_remove_no_tracks(self, spotify_client: SpotifyClient, new_playlist):
        assert "snapshot_id" in spotify_client.remove_playlist_items(new_playlist.id, [])

    def test_remove_track_list_upper_limit(self, spotify_client: SpotifyClient, new_playlist, track_uris):
        max_track_uris = [track_uris[0]] * 100
        spotify_client.add_tracks_to_playlist(new_playlist.id, max_track_uris)

        response = spotify_client.remove_playlist_items(new_playlist.id, max_track_uris)
        assert "snapshot_id" in response

    def test_get_all_current_user_playlists(self, spotify_client: SpotifyClient):
        playlists = list(spotify_client.get_current_user_playlists())
        assert all(isinstance(p, SimplifiedPlaylistObject) for p in playlists)

    def test_get_limited_number_of_current_use_playlists(self, spotify_client: SpotifyClient):
        limited_playlists = list(spotify_client.get_current_user_playlists(max_items=5))

        assert len(limited_playlists) == 5
        assert all(isinstance(p, SimplifiedPlaylistObject) for p in limited_playlists)

    def test_get_zero_current_user_playlists(self, spotify_client: SpotifyClient):
        zero_playlists = list(spotify_client.get_current_user_playlists(max_items=0))

        assert len(zero_playlists) == 0

    def test_get_user_playlists(self, spotify_client: SpotifyClient, user_id: str):
        playlists = list(spotify_client.get_user_playlists(user_id))
        assert all(isinstance(p, SimplifiedPlaylistObject) for p in playlists)

    def test_get_limited_number_of_user_playlists(self, spotify_client: SpotifyClient, user_id: str):
        limited_playlists = list(spotify_client.get_user_playlists(user_id, max_items=2))

        assert len(limited_playlists) == 2
        assert all(isinstance(p, SimplifiedPlaylistObject) for p in limited_playlists)

    def test_get_zero_user_playlists(self, spotify_client: SpotifyClient, user_id: str):
        zero_playlists = list(spotify_client.get_user_playlists(user_id, max_items=0))

        assert len(zero_playlists) == 0

    def test_get_nonexistent_user_playlists(self, spotify_client: SpotifyClient, non_existent_user_id: str):
        with pytest.raises(ResourceNotFoundException):
            list(spotify_client.get_user_playlists(non_existent_user_id))

    def test_get_all_featured_playlists(self, spotify_client: SpotifyClient):
        playlists = spotify_client.get_featured_playlists()
        assert isinstance(playlists, Generator)
        assert all(isinstance(p, SimplifiedPlaylistObject) for p in playlists)

    def test_get_limited_number_of_featured_playlists(self, spotify_client: SpotifyClient):
        limited_playlists = list(spotify_client.get_featured_playlists(max_items=5))
        assert len(limited_playlists) == 5
        assert all(isinstance(p, SimplifiedPlaylistObject) for p in limited_playlists)

    def test_get_zero_featured_playlists(self, spotify_client: SpotifyClient):
        zero_playlists = list(spotify_client.get_featured_playlists(max_items=0))
        assert len(zero_playlists) == 0

    def test_get_all_category_playlists(self, spotify_client: SpotifyClient):
        playlists = spotify_client.get_category_playlists(category="dinner")

        assert isinstance(playlists, Generator)
        assert all(isinstance(p, SimplifiedPlaylistObject) for p in playlists)

    def test_get_limited_number_of_category_playlists(self, spotify_client: SpotifyClient):
        limited_playlists = list(spotify_client.get_category_playlists(category="dinner", max_items=5))

        assert len(limited_playlists) == 5
        assert all(isinstance(p, SimplifiedPlaylistObject) for p in limited_playlists)

    def test_get_zero_category_playlists(self, spotify_client: SpotifyClient):
        zero_playlists = list(spotify_client.get_category_playlists(category="dinner", max_items=0))
        assert len(zero_playlists) == 0

    def test_invalid_category_id(self, spotify_client: SpotifyClient):
        with pytest.raises(ResourceNotFoundException):
            list(spotify_client.get_category_playlists(category="invalid_id"))

    def test_get_playlist_cover_image(self, spotify_client: SpotifyClient, playlist_id: str):
        images = spotify_client.get_playlist_cover_image(playlist=playlist_id)

        assert isinstance(images, list)
        assert all(isinstance(image, ImageObject) for image in images)

    def test_get_empty_playlist_cover_image(self, spotify_client: SpotifyClient, new_playlist: Playlist):
        images = spotify_client.get_playlist_cover_image(playlist=new_playlist.id)
        assert images == []

    def test_get_nonexistent_playlist_cover_image(self, spotify_client: SpotifyClient, non_existent_playlist_id: str):
        with pytest.raises(ResourceNotFoundException):  # Replace with your actual Exception
            spotify_client.get_playlist_cover_image(playlist=non_existent_playlist_id)

    def test_add_valid_cover(self, spotify_client, new_playlist, playlist_cover_image):
        assert not spotify_client.add_custom_playlist_cover_image(new_playlist.id, playlist_cover_image)
        time.sleep(2)
        assert len(spotify_client.get_playlist_cover_image(new_playlist.id)) == 1

    def test_add_valid_cover_to_non_existent_playlist(
        self, spotify_client, playlist_cover_image, non_existent_playlist_id
    ):
        with pytest.raises(ResourceNotFoundException):  # Replace with your expected exception
            spotify_client.add_custom_playlist_cover_image(non_existent_playlist_id, playlist_cover_image)

    def test_add_oversized_cover(self, spotify_client, new_playlist, invalid_playlist_cover_image):
        with pytest.raises(ValueError, match="Encoded image data exceeds 256 KB."):
            spotify_client.add_custom_playlist_cover_image(new_playlist.id, invalid_playlist_cover_image)

    def test_add_non_existent_cover_path(self, spotify_client, new_playlist, non_existent_playlist_cover_image):
        with pytest.raises(FileNotFoundError):
            spotify_client.add_custom_playlist_cover_image(new_playlist.id, non_existent_playlist_cover_image)
