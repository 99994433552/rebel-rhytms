import pytest
from rebel_rhythms import SpotifyClient, Track, ResourceNotFoundException, SavedTrackObject
from typing import Generator

from rebel_rhythms.models import AudioAnalysisObject, AudioFeaturesObject


class TestTrack:
    def test_get_valid_track(self, spotify_client: SpotifyClient, valid_track: str):
        track = spotify_client.get_track(valid_track)
        assert track is not None
        assert isinstance(track, Track)
        assert track.id == valid_track

    def test_get_non_existent_track(self, spotify_client, non_existent_track):
        with pytest.raises(ResourceNotFoundException):
            spotify_client.get_track(non_existent_track)

    def test_get_track_with_none(self, spotify_client):
        with pytest.raises(TypeError, match="missing 1 required positional argument: 'track'"):
            spotify_client.get_track(track=None)

    def test_get_several_tracks(self, spotify_client, multiple_valid_tracks):
        tracks = spotify_client.get_tracks(multiple_valid_tracks)
        assert tracks is not None
        assert isinstance(tracks, list)
        assert len(tracks) == 2
        assert all(isinstance(track, Track) for track in tracks)

    def test_get_single_track_using_multiple_track_request(self, spotify_client, valid_track):
        tracks = spotify_client.get_tracks(valid_track)
        assert tracks is not None
        assert isinstance(tracks, list)
        assert len(tracks) == 1
        assert all(isinstance(track, Track) for track in tracks)
        assert tracks[0].id == valid_track

    def test_get_tracks_with_none(self, spotify_client):
        with pytest.raises(TypeError, match="missing 1 required positional argument: 'tracks'"):
            spotify_client.get_tracks(tracks=None)

    def test_get_single_non_existing_track_using_multiple_track_request(self, spotify_client, non_existent_track):
        assert not spotify_client.get_tracks(non_existent_track)

    def test_get_mixed_tracks(self, spotify_client, mixed_tracks):
        tracks = spotify_client.get_tracks(mixed_tracks)
        assert tracks is not None
        assert isinstance(tracks, list)
        assert len(tracks) == 1
        assert all(isinstance(track, Track) for track in tracks)
        assert tracks[0].id == mixed_tracks[1]

    def test_get_multiple_tracks_with_same_id(self, spotify_client, valid_track):
        tracks = spotify_client.get_tracks([valid_track, valid_track])
        assert tracks is not None
        assert isinstance(tracks, list)
        assert len(tracks) == 2
        assert all(isinstance(track, Track) for track in tracks)
        assert all(track.id == valid_track for track in tracks)

    def test_get_tracks_with_empty_list(self, spotify_client):
        with pytest.raises(ValueError, match="ID or URL should not be empty."):
            spotify_client.get_tracks([])

    def test_get_multiple_tracks_with_max_limit(self, spotify_client, valid_track):
        tracks = spotify_client.get_tracks([valid_track] * 50)
        assert tracks is not None
        assert isinstance(tracks, list)
        assert len(tracks) == 50
        assert all(isinstance(track, Track) for track in tracks)
        assert all(track.id == valid_track for track in tracks)

    def test_get_multiple_tracks_with_more_than_max_limit(self, spotify_client, valid_track):
        with pytest.raises(ValueError, match="Too many IDs provided. Maximum allowed is 50."):
            spotify_client.get_tracks([valid_track] * 51)

    def test_get_user_saved_tracks(self, spotify_client):
        tracks = spotify_client.get_user_saved_tracks()
        assert isinstance(tracks, Generator)
        for item in tracks:
            assert isinstance(item, SavedTrackObject)

    def test_get_user_saved_tracks_with_limit_request(self, spotify_client):
        tracks = spotify_client.get_user_saved_tracks(max_items=10)
        assert isinstance(tracks, Generator)
        assert len(list(tracks)) == 10
        for item in tracks:
            assert isinstance(item, SavedTrackObject)

    def test_save_valid_track_to_current_user(self, spotify_client, valid_track):
        spotify_client.save_tracks_for_current_user(valid_track)
        tracks = spotify_client.get_user_saved_tracks()
        assert isinstance(tracks, Generator)
        assert any(item.track.id == valid_track for item in tracks)

    def test_save_multiple_valid_tracks_to_current_user(self, spotify_client, multiple_valid_tracks):
        spotify_client.save_tracks_for_current_user(multiple_valid_tracks)
        tracks = spotify_client.get_user_saved_tracks(max_items=10)
        assert isinstance(tracks, Generator)
        assert set(multiple_valid_tracks).issubset(set(item.track.id for item in tracks))

    def test_save_mixed_tracks_to_current_user(self, spotify_client, mixed_tracks):
        spotify_client.save_tracks_for_current_user(mixed_tracks)
        tracks = spotify_client.get_user_saved_tracks(max_items=10)
        assert isinstance(tracks, Generator)
        assert mixed_tracks[1] in set(item.track.id for item in tracks)
        assert not mixed_tracks[0] in set(item.track.id for item in tracks)

    def test_save_tracks_with_empty_list(self, spotify_client):
        with pytest.raises(ValueError, match="ID or URL should not be empty."):
            spotify_client.save_tracks_for_current_user([])

    def test_save_tracks_with_exceeding_limit(self, spotify_client, valid_track):
        with pytest.raises(ValueError, match="Too many IDs provided. Maximum allowed is 50."):
            spotify_client.save_tracks_for_current_user([valid_track] * 51)

    def test_get_track_audio_features(self, spotify_client, valid_track):
        features = spotify_client.get_track_audio_features(valid_track)
        assert features is not None
        assert isinstance(features, AudioFeaturesObject)

    def test_get_non_extistent_track_audio_features(self, spotify_client, non_existent_track):
        with pytest.raises(ResourceNotFoundException):
            spotify_client.get_track_audio_features(non_existent_track)

    def test_get_track_audio_analysis(self, spotify_client, valid_track):
        analysis = spotify_client.get_track_audio_analysis(valid_track)
        assert analysis is not None
        assert isinstance(analysis, AudioAnalysisObject)

    def test_get_non_extistent_track_audio_analysis(self, spotify_client, non_existent_track):
        with pytest.raises(ResourceNotFoundException):
            spotify_client.get_track_audio_analysis(non_existent_track)

    def test_remove_user_saved_tracks(self, spotify_client, valid_track):
        spotify_client.save_tracks_for_current_user(valid_track)
        tracks = spotify_client.get_user_saved_tracks(max_items=10)
        assert valid_track in set(item.track.id for item in tracks)

        spotify_client.remove_user_saved_tracks(valid_track)
        tracks = spotify_client.get_user_saved_tracks()
        assert valid_track not in set(item.track.id for item in tracks)

    def test_remove_user_saved_tracks_with_multiple_tracks(self, spotify_client, multiple_valid_tracks):
        spotify_client.save_tracks_for_current_user(multiple_valid_tracks)
        tracks = spotify_client.get_user_saved_tracks(max_items=10)
        assert set(multiple_valid_tracks).issubset(set(item.track.id for item in tracks))

        spotify_client.remove_user_saved_tracks(multiple_valid_tracks)
        tracks = spotify_client.get_user_saved_tracks()
        assert not set(multiple_valid_tracks).issubset(set(item.track.id for item in tracks))

    def test_remove_user_saved_tracks_with_non_existent_track(self, spotify_client, non_existent_track):
        assert not spotify_client.remove_user_saved_tracks(non_existent_track)

    def test_user_saved_tracks(self, spotify_client, valid_track):
        spotify_client.save_tracks_for_current_user(valid_track)
        assert spotify_client.check_user_saved_tracks(valid_track) == [True]

    def test_user_saved_tracks_with_multiple_tracks(self, spotify_client, multiple_valid_tracks):
        spotify_client.save_tracks_for_current_user(multiple_valid_tracks)
        assert spotify_client.check_user_saved_tracks(multiple_valid_tracks) == [True, True]

    def test_user_saved_tracks_with_non_existent_track(self, spotify_client, non_existent_track):
        assert spotify_client.check_user_saved_tracks(non_existent_track) == [False]

    def test_user_saved_tracks_with_mixed_tracks(self, spotify_client, mixed_tracks):
        spotify_client.save_tracks_for_current_user(mixed_tracks)
        assert spotify_client.check_user_saved_tracks(mixed_tracks) == [False, True]
