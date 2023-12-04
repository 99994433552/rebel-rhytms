import pytest
from rebel_rhythms.validators import (
    check_list_limit,
    validate_track_uris,
    validate_id_or_url,
    ContentType,
)
import re


# Test for function that checks list limit
def test_check_list_limit():
    # Decorate a function with check_list_limit, the maximum allowed limit is 3
    @check_list_limit("my_list", 3)
    def limited_func(my_list):
        return len(my_list)

    # Test that function returns the length of the list when the limit is not exceeded
    assert limited_func([1, 2, 3]) == 3

    # Test that function raises ValueError when the limit is exceeded
    with pytest.raises(ValueError, match="Too many IDs provided. Maximum allowed is 3"):
        limited_func([1, 2, 3, 4])


# Test for function that validates track URIs
def test_validate_track_uris():
    assert validate_track_uris("spotify:track:1234567890123456789012") == ["spotify:track:1234567890123456789012"]

    # Test that function raises ValueError when the URI is invalid
    with pytest.raises(ValueError, match="Invalid track URI: invalid_uri"):
        validate_track_uris("invalid_uri")


# Mock class to simulate the behavior of real objects
class MockClass:
    # Define methods decorated with validate_id_or_url
    @validate_id_or_url(ContentType.TRACK, multiple=True)
    def mock_method_track_multiple(self, ids):
        return ids

    @validate_id_or_url(ContentType.ALBUM, multiple=True)
    def mock_method_album_multiple(self, ids):
        return ids

    @validate_id_or_url(ContentType.PLAYLIST, multiple=True)
    def mock_method_playlist_multiple(self, ids):
        return ids

    @validate_id_or_url(ContentType.TRACK, multiple=False)
    def mock_method_track_single(self, ids):
        return ids

    @validate_id_or_url(ContentType.ALBUM, multiple=False)
    def mock_method_album_single(self, ids):
        return ids

    @validate_id_or_url(ContentType.PLAYLIST, multiple=False)
    def mock_method_playlist_single(self, ids):
        return ids


@pytest.mark.parametrize(
    "content_type, method_name",
    [
        (ContentType.TRACK, "mock_method_track_multiple"),
        (ContentType.ALBUM, "mock_method_album_multiple"),
        (ContentType.PLAYLIST, "mock_method_playlist_multiple"),
        (ContentType.TRACK, "mock_method_track_single"),
        (ContentType.ALBUM, "mock_method_album_single"),
        (ContentType.PLAYLIST, "mock_method_playlist_single"),
    ],
)
def test_validate_id_or_url(content_type, method_name):
    obj = MockClass()  # Create an instance of MockClass

    # Test for methods that accept multiple IDs
    if "multiple" in method_name:
        assert getattr(obj, method_name)(["1234567890123456789012", "1234567890123456789013"]) == [
            "1234567890123456789012",
            "1234567890123456789013",
        ]
    # Test for methods that accept a single ID
    else:
        assert getattr(obj, method_name)("1234567890123456789012") == "1234567890123456789012"

    # Test that it raises an error with invalid input
    invalid_input = "invalid"
    with pytest.raises(ValueError, match=rf"Invalid ID or URL: {re.escape(invalid_input)}"):
        getattr(obj, method_name)(invalid_input)

    # Additional case when multiple=False
    if "single" in method_name:
        invalid_list_input = ["1234567890123456789012", "invalid"]
        with pytest.raises(ValueError, match=rf"Invalid ID or URL: {re.escape(str(invalid_list_input))}"):
            getattr(obj, method_name)(invalid_list_input)
