from rebel_rhythms import SpotifyClient, BrowseCategory, ResourceNotFoundException
import pytest


class TestCategory:
    def test_get_browse_categories(self, spotify_client: SpotifyClient):
        categories = list(spotify_client.get_browse_categories())
        assert len(categories) == 40
        assert all(isinstance(category, BrowseCategory) for category in categories)

    def test_get_limited_browse_categories(self, spotify_client: SpotifyClient):
        categories = list(spotify_client.get_browse_categories(max_items=10))
        assert len(categories) == 10
        assert all(isinstance(category, BrowseCategory) for category in categories)

    def test_get_single_browse_category(self, spotify_client: SpotifyClient):
        category = spotify_client.get_browse_category("toplists")
        assert isinstance(category, BrowseCategory)
        assert category.id == "toplists"

    def test_get_non_existent_browse_category(self, spotify_client: SpotifyClient):
        with pytest.raises(ResourceNotFoundException):
            spotify_client.get_browse_category("non-existent")
