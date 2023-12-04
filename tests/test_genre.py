from rebel_rhythms import SpotifyClient, BrowseCategory, ResourceNotFoundException


class TestGenre:
    def test_get_available_genre_seeds(self, spotify_client: SpotifyClient):
        genres = spotify_client.get_available_genre_seeds()
        assert len(genres) > 0
        assert all(isinstance(genre, str) for genre in genres)
        assert "pop" in genres
