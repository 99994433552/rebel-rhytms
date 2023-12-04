import pytest
from rebel_rhythms import AlbumObject, SimplifiedTrackObject, SavedAlbumObject
from rebel_rhythms.custom_exceptions import ResourceNotFoundException
from rebel_rhythms.models import SimplifiedAlbumObject
from types import GeneratorType as Generator


class TestAlbum:
    def test_get_album(self, spotify_client, album_id):
        actual_album = spotify_client.get_album(album_id)
        assert isinstance(actual_album, AlbumObject)

    def test_get_non_existing_album(self, spotify_client, non_existent_album_id):
        with pytest.raises(ResourceNotFoundException):
            spotify_client.get_album(non_existent_album_id)

    def test_get_multiple_albums(self, spotify_client, multiple_album_ids):
        actual_albums = spotify_client.get_albums(multiple_album_ids)
        assert isinstance(actual_albums, list)
        assert all(isinstance(album, AlbumObject) for album in actual_albums)

    def test_get_multiple_albums_with_exceeding_limit(self, spotify_client, album_id):
        with pytest.raises(ValueError, match="Too many IDs provided. Maximum allowed is 20."):
            spotify_client.get_albums([album_id] * 21)

    def test_get_multiple_albums_with_max_limit(self, spotify_client, album_id):
        actual_albums = spotify_client.get_albums([album_id] * 20)
        assert isinstance(actual_albums, list)
        assert all(isinstance(album, AlbumObject) for album in actual_albums)

    def test_get_multiple_not_existing_albums(self, spotify_client, non_existent_album_id):
        assert not spotify_client.get_albums([non_existent_album_id])

    def test_get_multiple_albums_one_of_which_is_non_existent(
        self, spotify_client, multiple_album_ids, non_existent_album_id
    ):
        actual_albums = spotify_client.get_albums(multiple_album_ids + [non_existent_album_id])
        assert isinstance(actual_albums, list)
        assert len(actual_albums) == 2
        assert all(isinstance(album, AlbumObject) for album in actual_albums)

    def test_get_all_album_tracks(self, spotify_client, album_id):
        actual_tracks = spotify_client.get_album_tracks(album_id)
        assert isinstance(actual_tracks, Generator)
        assert len(list(actual_tracks)) == 10
        assert all(isinstance(track, SimplifiedTrackObject) for track in actual_tracks)

    def test_get_album_tracks_with_limited_response(self, spotify_client, album_id):
        actual_tracks = spotify_client.get_album_tracks(album_id, max_items=2)
        assert isinstance(actual_tracks, Generator)
        assert len(list(actual_tracks)) == 2
        assert all(isinstance(track, SimplifiedTrackObject) for track in actual_tracks)

    def test_get_user_saved_albums(self, spotify_client):
        actual_saved_albums = spotify_client.get_user_saved_albums()
        assert isinstance(actual_saved_albums, Generator)
        assert all(isinstance(album, SavedAlbumObject) for album in actual_saved_albums)

    def test_get_user_saved_albums_with_limited_response(self, spotify_client):
        actual_saved_albums = spotify_client.get_user_saved_albums(max_items=2)
        assert isinstance(actual_saved_albums, Generator)
        assert len(list(actual_saved_albums)) == 2
        assert all(isinstance(album, SavedAlbumObject) for album in actual_saved_albums)

    def test_save_album(self, spotify_client, album_id):
        assert not spotify_client.save_albums([album_id])

    def test_save_non_existing_album(self, spotify_client, non_existent_album_id):
        assert not spotify_client.save_albums([non_existent_album_id])

    def test_save_multiple_albums(self, spotify_client, multiple_album_ids):
        assert not spotify_client.save_albums(multiple_album_ids)

    def test_save_multiple_albums_with_exceeding_limit(self, spotify_client, album_id):
        with pytest.raises(ValueError, match="Too many IDs provided. Maximum allowed is 50."):
            spotify_client.save_albums([album_id] * 51)

    def test_save_multiple_albums_with_max_limit(self, spotify_client, album_id):
        assert not spotify_client.save_albums([album_id] * 50)

    def test_save_multiple_albums_one_of_which_is_non_existent(
        self, spotify_client, multiple_album_ids, non_existent_album_id
    ):
        assert not spotify_client.save_albums(multiple_album_ids + [non_existent_album_id])

    def test_save_multiple_non_existing_albums(self, spotify_client, non_existent_album_id):
        assert not spotify_client.save_albums([non_existent_album_id, non_existent_album_id])

    def test_remove_user_saved_album(self, spotify_client, album_id):
        assert not spotify_client.remove_user_saved_albums(album_id)

    def test_remove_non_existing_user_saved_album(self, spotify_client, non_existent_album_id):
        assert not spotify_client.remove_user_saved_albums(non_existent_album_id)

    def test_remove_multiple_user_saved_albums(self, spotify_client, multiple_album_ids):
        assert not spotify_client.remove_user_saved_albums(multiple_album_ids)

    def test_remove_multiple_user_saved_albums_one_of_which_is_non_existent(
        self, spotify_client, multiple_album_ids, non_existent_album_id
    ):
        assert not spotify_client.remove_user_saved_albums(multiple_album_ids + [non_existent_album_id])

    def test_remove_maximum_user_saved_albums(self, spotify_client, album_id):
        assert not spotify_client.remove_user_saved_albums([album_id] * 50)

    def test_remove_multiple_user_saved_albums_with_exceeding_limit(self, spotify_client, album_id):
        with pytest.raises(ValueError, match="Too many IDs provided. Maximum allowed is 50."):
            spotify_client.remove_user_saved_albums([album_id] * 51)

    def test_remove_multiple_non_existing_user_saved_albums(self, spotify_client, non_existent_album_id):
        assert not spotify_client.remove_user_saved_albums([non_existent_album_id, non_existent_album_id])

    def test_check_user_saved_albums(self, spotify_client, album_id):
        spotify_client.save_albums(album_id)
        assert spotify_client.check_user_saved_albums(album_id)

    def test_check_non_existing_user_saved_albums(self, spotify_client, non_existent_album_id):
        assert spotify_client.check_user_saved_albums(non_existent_album_id) == [False]

    def test_check_user_not_saved_albums(self, spotify_client, album_id):
        spotify_client.remove_user_saved_albums(album_id)
        assert spotify_client.check_user_saved_albums(album_id) == [False]

    def test_check_multiple_user_saved_albums(self, spotify_client, multiple_album_ids):
        spotify_client.save_albums(multiple_album_ids)
        assert spotify_client.check_user_saved_albums(multiple_album_ids)

    def test_check_multiple_non_existing_user_saved_albums(self, spotify_client, non_existent_album_id):
        assert spotify_client.check_user_saved_albums([non_existent_album_id, non_existent_album_id]) == [False]

    def test_check_user_saved_albums_with_exceeding_limit(self, spotify_client, album_id):
        with pytest.raises(ValueError, match="Too many IDs provided. Maximum allowed is 20."):
            spotify_client.check_user_saved_albums([album_id] * 21)

    def test_get_user_saved_albums_with_max_limit(self, spotify_client, album_id):
        assert spotify_client.check_user_saved_albums([album_id] * 20) == [True]

    def test_get_new_releases(self, spotify_client):
        actual_albums = spotify_client.get_new_releases()
        assert isinstance(actual_albums, Generator)
        assert all(isinstance(album, SimplifiedAlbumObject) for album in actual_albums)

    def test_get_new_releases_with_limited_response(self, spotify_client):
        actual_albums = spotify_client.get_new_releases(max_items=2)
        assert isinstance(actual_albums, Generator)
        assert len(list(actual_albums)) == 2
        assert all(isinstance(album, SimplifiedAlbumObject) for album in actual_albums)
