import base64
import random
from collections import defaultdict
from enum import Enum
from typing import Dict, Generator, List, Optional, Type, Union

from rebel_rhythms.models import (
    AlbumObject,
    ArtistObject,
    AudioAnalysisObject,
    AudioFeaturesObject,
    BrowseCategory,
    CurrentUser,
    ImageObject,
    Playlist,
    PlaylistTrackObject,
    Recommendations,
    SavedAlbumObject,
    SavedTrackObject,
    SimplifiedAlbumObject,
    SimplifiedPlaylistObject,
    SimplifiedTrackObject,
    Track,
    User,
)
from rebel_rhythms.spotify_auth import SpotifyAuth
from rebel_rhythms.spotify_request_manager import SpotifyRequestManager
from rebel_rhythms.validators import (
    ContentType,
    check_list_limit,
    validate_boolean_param,
    validate_id_or_url,
    validate_playlist_params,
    validate_track_uris,
)


class IncludeGroups(Enum):
    ALBUM = "album"
    SINGLE = "single"
    APPEARS_ON = "appears_on"
    COMPILATION = "compilation"


class ItemsType(str, Enum):
    ARTISTS = "artists"
    TRACKS = "tracks"


class SpotifyClient:
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri="http://localhost:8080/callback",
        market="UA",
        scope=None,
    ):
        self.market = market
        self.spotify_auth = SpotifyAuth(
            client_id, client_secret, redirect_uri=redirect_uri, scope=scope
        )
        self.request_manager = SpotifyRequestManager(self.spotify_auth, self.market)

    def _format_ids(self, ids: Union[str, List[str]]) -> str:
        if isinstance(ids, list):
            return ",".join(ids)
        else:
            return ids

    def _build_search_query(self, query_dict: dict) -> str:
        return "-".join([f'{k}:"{v}"' for k, v in query_dict.items()])

    # [Tested]
    @validate_id_or_url(ContentType.ALBUM, multiple=False)
    def get_album(self, album: str) -> AlbumObject:
        response = self.request_manager.get(f"/v1/albums/{album}")
        return AlbumObject(**response)

    # [Tested]
    @check_list_limit("albums", 20)
    @validate_id_or_url(ContentType.ALBUM, multiple=True)
    def get_albums(self, albums: List[str]) -> List[AlbumObject]:
        response = self.request_manager.get(
            "/v1/albums", params={"ids": ",".join(albums)}
        )
        return [
            AlbumObject(**album)
            for album in response.get("albums", [])
            if album is not None
        ]

    # [Tested]
    @validate_id_or_url(ContentType.ALBUM, multiple=False)
    def get_album_tracks(
        self, album: str, max_items: Optional[int] = None
    ) -> Generator[SimplifiedTrackObject, None, None]:
        endpoint = f"/v1/albums/{album}/tracks"
        params = {"limit": 50, "offset": 0}

        if max_items is None:
            return self.request_manager._fetch_from_api(
                endpoint, params, lambda item: SimplifiedTrackObject(**item)
            )
        else:
            return self.request_manager._fetch_limited_from_api(
                endpoint, params, lambda item: SimplifiedTrackObject(**item), max_items
            )

    # [Tested]
    def get_user_saved_albums(
        self, max_items: Optional[int] = None
    ) -> Generator[SavedAlbumObject, None, None]:
        endpoint = "/v1/me/albums"
        params = {"limit": 50, "offset": 0}

        if max_items is None:
            return self.request_manager._fetch_from_api(
                endpoint, params, lambda item: SavedAlbumObject(**item)
            )
        else:
            return self.request_manager._fetch_limited_from_api(
                endpoint, params, lambda item: SavedAlbumObject(**item), max_items
            )

    # [Tested]
    @check_list_limit("albums", 50)
    @validate_id_or_url(ContentType.ALBUM, multiple=True)
    def save_albums(self, albums: Union[str, list[str]]) -> None:
        response = self.request_manager.put("/v1/me/albums", json={"ids": albums})
        return response

    # [Tested]
    @check_list_limit("albums", 50)
    @validate_id_or_url(ContentType.ALBUM, multiple=True)
    def remove_user_saved_albums(self, albums: Union[str, list[str]]) -> None:
        response = self.request_manager.delete("/v1/me/albums", json={"ids": albums})
        return response

    # [Tested]
    @check_list_limit("albums", 20)
    @validate_id_or_url(ContentType.ALBUM, multiple=True)
    def check_user_saved_albums(self, albums: Union[str, list[str]]) -> List[bool]:
        response = self.request_manager.get(
            "/v1/me/albums/contains", params={"ids": albums}
        )
        return response

    # [Tested]
    def get_new_releases(
        self, max_items: Optional[int] = None
    ) -> Generator[SimplifiedAlbumObject, None, None]:
        endpoint = "/v1/browse/new-releases"
        params = {"limit": 50, "offset": 0}

        if max_items is None:
            return self.request_manager._fetch_from_api(
                endpoint,
                params,
                lambda item: SimplifiedAlbumObject(**item),
                item_path="albums.items",
                next_path="albums.next",
            )
        else:
            return self.request_manager._fetch_limited_from_api(
                endpoint,
                params,
                lambda item: SimplifiedAlbumObject(**item),
                max_items,
                item_path="albums.items",
                next_path="albums.next",
            )

    # [Tested]
    @validate_id_or_url(ContentType.ARTIST, multiple=False)
    def get_artist(self, artist: str) -> ArtistObject:
        response = self.request_manager.get(f"/v1/artists/{artist}")
        return ArtistObject(**response)

    # [Tested]
    @check_list_limit("artists", 50)
    @validate_id_or_url(ContentType.ARTIST, multiple=True)
    def get_artists(self, artists: List[str]) -> List[ArtistObject]:
        response = self.request_manager.get(
            "/v1/artists", params={"ids": ",".join(artists)}, include_market=False
        )
        return [
            ArtistObject(**artist) for artist in response.get("artists", []) if artist
        ]

    # [Tested]
    @validate_id_or_url(ContentType.ARTIST, multiple=False)
    def get_artist_albums(
        self,
        artist: str,
        include_groups: Optional[List[IncludeGroups]] = None,
        max_items: Optional[int] = None,
    ) -> Generator[SimplifiedAlbumObject, None, None]:
        endpoint = f"/v1/artists/{artist}/albums"
        params = {"limit": 50, "offset": 0}

        if include_groups:
            for group in include_groups:
                if not isinstance(group, IncludeGroups):
                    raise TypeError(
                        "include_groups must be a list of IncludeGroups enum instances"
                    )

            params["include_groups"] = ",".join(group.value for group in include_groups)

        if max_items is None:
            return self.request_manager._fetch_from_api(
                endpoint,
                params,
                lambda item: SimplifiedAlbumObject(**item),
            )
        else:
            return self.request_manager._fetch_limited_from_api(
                endpoint,
                params,
                lambda item: SimplifiedAlbumObject(**item),
                max_items,
            )

    # [Tested]
    @validate_id_or_url(ContentType.ARTIST, multiple=False)
    def get_artist_top_tracks(self, artist: str) -> List[Track]:
        response = self.request_manager.get(f"/v1/artists/{artist}/top-tracks")
        return [Track(**item) for item in response.get("tracks", [])]

    # [Tested]
    @validate_id_or_url(content_type=ContentType.ARTIST, multiple=False)
    def get_related_artists(self, artist: str) -> List[ArtistObject]:
        response = self.request_manager.get(f"/v1/artists/{artist}/related-artists")
        return [ArtistObject(**item) for item in response.get("artists", [])]

    # [Tested]
    def get_browse_categories(
        self, max_items: Optional[int] = None
    ) -> Generator[BrowseCategory, None, None]:
        endpoint = "/v1/browse/categories"
        params = {"limit": 50, "offset": 0}

        if max_items is None:
            return self.request_manager._fetch_from_api(
                endpoint,
                params,
                lambda item: BrowseCategory(**item),
                item_path="categories.items",
                next_path="categories.next",
            )
        else:
            return self.request_manager._fetch_limited_from_api(
                endpoint,
                params,
                lambda item: BrowseCategory(**item),
                max_items,
                item_path="categories.items",
                next_path="categories.next",
            )

    # [Tested]
    def get_browse_category(self, category_id: str) -> BrowseCategory:
        response = self.request_manager.get(
            f"/v1/browse/categories/{category_id}", params={"country": self.market}
        )
        return BrowseCategory(**response)

    # [Tested]
    def get_available_genre_seeds(self) -> List[str]:
        response = self.request_manager.get("/v1/recommendations/available-genre-seeds")
        return response.get("genres", [])

    # [Tested]
    @validate_id_or_url(content_type=ContentType.PLAYLIST, multiple=False)
    def get_playlist(self, playlist: str) -> Playlist:
        response = self.request_manager.get(f"/v1/playlists/{playlist}")
        return Playlist(**response)

    # [Tested]
    def create_playlist(
        self,
        name: str,
        description: Optional[str] = None,
        public: bool = True,
        collaborative: bool = False,
    ) -> Playlist:
        validate_boolean_param(public, "public")
        validate_boolean_param(collaborative, "collaborative")
        validate_playlist_params(public, collaborative)

        response = self.request_manager.post(
            f"/v1/me/playlists",
            json=dict(
                name=name,
                public=public,
                collaborative=collaborative,
                description=description,
            ),
        )
        return Playlist(**response)

    # [Tested]
    @validate_id_or_url(content_type=ContentType.PLAYLIST, multiple=False)
    def change_playlist_details(
        self,
        playlist: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        public: Optional[bool] = None,
        collaborative: Optional[bool] = None,
    ) -> None:
        validate_boolean_param(public, "public")
        validate_boolean_param(collaborative, "collaborative")
        validate_playlist_params(public, collaborative)

        payload = {
            key: value
            for key, value in [
                ("name", name),
                ("description", description),
                ("public", public),
                ("collaborative", collaborative),
            ]
            if value is not None
        }

        return self.request_manager.put(f"/v1/playlists/{playlist}", json=payload)

    # [Tested]
    @validate_id_or_url(content_type=ContentType.PLAYLIST, multiple=False)
    def get_all_playlist_tracks(
        self, playlist: str, max_items: Optional[int] = None
    ) -> Generator[PlaylistTrackObject, None, None]:
        endpoint = f"/v1/playlists/{playlist}/tracks"
        params = {"limit": 50, "offset": 0}

        if max_items is None:
            return self.request_manager._fetch_from_api(
                endpoint,
                params,
                lambda item: PlaylistTrackObject(**item),
            )
        else:
            return self.request_manager._fetch_limited_from_api(
                endpoint,
                params,
                lambda item: PlaylistTrackObject(**item),
                max_items,
            )

    # [Tested]
    @check_list_limit("uris", 100)
    @validate_id_or_url(content_type=ContentType.PLAYLIST, multiple=False)
    def add_tracks_to_playlist(
        self,
        playlist: str,
        uris: List[str],
        position: Optional[int] = None,
    ) -> Dict:
        if position and position < 0:
            raise ValueError("Invalid position, must be positive.")
        return self.request_manager.post(
            f"/v1/playlists/{playlist}/tracks",
            json=dict(uris=validate_track_uris(uris), position=position),
        )

    # [Tested]
    @check_list_limit("uris", 100)
    @validate_id_or_url(content_type=ContentType.PLAYLIST, multiple=False)
    def remove_playlist_items(self, playlist: str, uris: Union[str, List[str]]) -> Dict:
        return self.request_manager.delete(
            f"/v1/playlists/{playlist}/tracks",
            json={
                "tracks": [
                    {"uri": track_uri} for track_uri in validate_track_uris(uris)
                ]
            },
        )

    # [Tested]
    def get_current_user_playlists(
        self, max_items: Optional[int] = None
    ) -> Union[
        Generator[SimplifiedPlaylistObject, None, None], List[SimplifiedPlaylistObject]
    ]:
        endpoint = "/v1/me/playlists"
        params = {"limit": 50, "offset": 0}

        if max_items is None:
            return self.request_manager._fetch_from_api(
                endpoint, params, lambda item: SimplifiedPlaylistObject(**item)
            )
        else:
            return self.request_manager._fetch_limited_from_api(
                endpoint,
                params,
                lambda item: SimplifiedPlaylistObject(**item),
                max_items,
            )

    # [Tested]
    @validate_id_or_url(content_type=ContentType.USER, multiple=False)
    def get_user_playlists(
        self, user: str, max_items: Optional[int] = None
    ) -> Union[
        Generator[SimplifiedPlaylistObject, None, None], List[SimplifiedPlaylistObject]
    ]:
        endpoint = f"/v1/users/{user}/playlists"
        params = {"limit": 50, "offset": 0}

        if max_items is None:
            return self.request_manager._fetch_from_api(
                endpoint, params, lambda item: SimplifiedPlaylistObject(**item)
            )
        else:
            return self.request_manager._fetch_limited_from_api(
                endpoint,
                params,
                lambda item: SimplifiedPlaylistObject(**item),
                max_items,
            )

    # [Tested]
    def get_featured_playlists(
        self, max_items: Optional[int] = None
    ) -> Generator[SimplifiedPlaylistObject, None, None]:
        endpoint = "/v1/browse/featured-playlists"
        params = {"limit": 50, "offset": 0}

        if max_items is None:
            return self.request_manager._fetch_from_api(
                endpoint,
                params,
                lambda item: SimplifiedPlaylistObject(**item),
                item_path="playlists.items",
                next_path="playlists.next",
            )
        else:
            return self.request_manager._fetch_limited_from_api(
                endpoint,
                params,
                lambda item: SimplifiedPlaylistObject(**item),
                max_items,
                item_path="playlists.items",
                next_path="playlists.next",
            )

    # [Tested]
    def get_category_playlists(
        self, category: str, max_items: Optional[int] = None
    ) -> Generator[SimplifiedPlaylistObject, None, None]:
        endpoint = f"/v1/browse/categories/{category}/playlists"
        params = {"limit": 50, "offset": 0}

        if max_items is None:
            return self.request_manager._fetch_from_api(
                endpoint,
                params,
                lambda item: SimplifiedPlaylistObject(**item),
                item_path="playlists.items",
                next_path="playlists.next",
            )
        else:
            return self.request_manager._fetch_limited_from_api(
                endpoint,
                params,
                lambda item: SimplifiedPlaylistObject(**item),
                max_items,
                item_path="playlists.items",
                next_path="playlists.next",
            )

    # [Tested]
    @validate_id_or_url(content_type=ContentType.PLAYLIST, multiple=False)
    def get_playlist_cover_image(self, playlist: str) -> Optional[List[ImageObject]]:
        response = self.request_manager.get(f"/v1/playlists/{playlist}/images")
        return [ImageObject(**image) for image in response]

    # [Tested]
    @validate_id_or_url(content_type=ContentType.PLAYLIST, multiple=False)
    def add_custom_playlist_cover_image(self, playlist: str, image_path: str) -> None:
        endpoint = f"/v1/playlists/{playlist}/images"

        with open(image_path, "rb") as image_file:
            base64_encoded_image = base64.b64encode(image_file.read()).decode("utf-8")

        encoded_image_size_kb = len(base64_encoded_image) * 3 / 4 / 1024
        if encoded_image_size_kb > 256:
            raise ValueError("Encoded image data exceeds 256 KB.")

        headers = {
            "Content-Type": "image/jpeg",
        }

        headers.update(self.request_manager.headers)

        return self.request_manager.put(
            endpoint, data=base64_encoded_image, headers=headers
        )

    # [Tested]
    @validate_id_or_url(content_type=ContentType.TRACK, multiple=False)
    def get_track(self, track: str) -> Track:
        response = self.request_manager.get(f"/v1/tracks/{track}")
        return Track(**response)

    # [Tested]
    @check_list_limit("tracks", 50)
    @validate_id_or_url(content_type=ContentType.TRACK, multiple=True)
    def get_tracks(self, tracks: List[str]) -> List[Track]:
        response = self.request_manager.get(
            f"/v1/tracks", params=dict(ids=",".join(tracks))
        )
        return [Track(**track) for track in response.get("tracks", []) if track]

    # [Tested]
    def get_user_saved_tracks(
        self, max_items: Optional[int] = None
    ) -> Generator[SavedTrackObject, None, None]:
        endpoint = "/v1/me/tracks"
        params = {"limit": 50, "offset": 0}
        if max_items is None:
            return self.request_manager._fetch_from_api(
                endpoint,
                params,
                lambda item: SavedTrackObject(**item),
            )
        else:
            return self.request_manager._fetch_limited_from_api(
                endpoint,
                params,
                lambda item: SavedTrackObject(**item),
                max_items,
            )

    # [Tested]
    @check_list_limit("tracks", 50)
    @validate_id_or_url(content_type=ContentType.TRACK, multiple=True)
    def save_tracks_for_current_user(self, tracks: Union[str, List[str]]) -> None:
        return self.request_manager.put("/v1/me/tracks", json=dict(ids=tracks))

    # [Tested]
    @check_list_limit("tracks", 50)
    @validate_id_or_url(content_type=ContentType.TRACK, multiple=True)
    def remove_user_saved_tracks(self, tracks: Union[str, List[str]]) -> None:
        return self.request_manager.delete("/v1/me/tracks", json=dict(ids=tracks))

    # [Tested]
    @check_list_limit("tracks", 50)
    @validate_id_or_url(content_type=ContentType.TRACK, multiple=True)
    def check_user_saved_tracks(self, tracks: Union[str, List[str]]) -> None:
        return self.request_manager.get(
            "/v1/me/tracks/contains", params=dict(ids=self._format_ids(tracks))
        )

    # [Tested]
    @check_list_limit("track_ids_or_urls", 100)
    def get_tracks_audio_features(
        self, track_ids_or_urls: Union[str, List[str]]
    ) -> List[AudioFeaturesObject]:
        track_ids_str = self._process_track_ids(track_ids_or_urls)
        response = self.get("/v1/audio-features", params=dict(ids=track_ids_str))
        return [
            AudioFeaturesObject(**item)
            for item in response.get("audio_features", [])
            if item is not None
        ]

    # [Tested]
    @validate_id_or_url(content_type=ContentType.TRACK, multiple=False)
    def get_track_audio_features(self, track: str) -> AudioFeaturesObject:
        response = self.request_manager.get(f"/v1/audio-features/{track}")
        return AudioFeaturesObject(**response)

    # [Tested]
    @validate_id_or_url(content_type=ContentType.TRACK, multiple=False)
    def get_track_audio_analysis(self, track: str) -> AudioAnalysisObject:
        response = self.request_manager.get(f"/v1/audio-analysis/{track}")
        return AudioAnalysisObject(**response)

    # [Tested]
    def get_current_user_profile(self) -> CurrentUser:
        response = self.request_manager.get("/v1/me")
        return CurrentUser(**response)

    # [Tested]
    def get_user_top_items(
        self,
        items_type: ItemsType = ItemsType.TRACKS,
        time_range: Optional[str] = "medium_term",
        max_items: Optional[int] = None,
    ) -> Union[Generator[Track, None, None], Generator[ArtistObject, None, None]]:
        if not isinstance(items_type, ItemsType):
            raise ValueError(
                "Invalid items_type. Must be an instance of ItemsType Enum."
            )

        valid_time_ranges = ["short_term", "medium_term", "long_term"]
        if time_range not in valid_time_ranges:
            raise ValueError(f"Invalid time_range. Must be one of {valid_time_ranges}.")

        endpoint = f"/v1/me/top/{items_type.value}"
        params = {"limit": 50, "offset": 0, "time_range": time_range}

        if max_items is None:
            return self.request_manager._fetch_from_api(
                endpoint,
                params,
                lambda item: Track(**item)
                if items_type == ItemsType.TRACKS
                else ArtistObject(**item),
                include_market=False,
            )
        else:
            return self.request_manager._fetch_limited_from_api(
                endpoint,
                params,
                lambda item: Track(**item)
                if items_type == ItemsType.TRACKS
                else ArtistObject(**item),
                max_items,
                include_market=False,
            )

    # [Tested]
    @validate_id_or_url(content_type=ContentType.USER, multiple=False)
    def get_user_profile(self, user_id: str) -> User:
        response = self.request_manager.get(f"/v1/users/{user_id}")
        return User(**response)

    # [Tested]
    @validate_id_or_url(content_type=ContentType.PLAYLIST, multiple=False)
    def follow_playlist(self, playlist: str, public: bool = False) -> None:
        return self.request_manager.put(
            f"/v1/playlists/{playlist}/followers", params={"public": public}
        )

    # [Tested]
    @validate_id_or_url(content_type=ContentType.PLAYLIST, multiple=False)
    def unfollow_playlist(self, playlist: str):
        return self.request_manager.delete(f"/v1/playlists/{playlist}/followers")

    # [Tested]
    def search(
        self,
        query: str,
        search_type: str,
        max_items: Optional[int] = None,
    ) -> Generator[
        Union[SimplifiedAlbumObject, ArtistObject, Track, SimplifiedPlaylistObject],
        None,
        None,
    ]:
        endpoint = "/v1/search"

        if isinstance(query, dict):
            query = self._build_search_query(query)

        params = {
            "q": query,
            "type": search_type,
            "limit": 50,
            "offset": 0,
        }

        result_type_map = {
            "album": {
                "obj": SimplifiedAlbumObject,
                "next_path": "albums.next",
                "item_path": "albums.items",
            },
            "artist": {
                "obj": ArtistObject,
                "next_path": "artists.next",
                "item_path": "artists.items",
            },
            "track": {
                "obj": Track,
                "next_path": "tracks.next",
                "item_path": "tracks.items",
            },
            "playlist": {
                "obj": SimplifiedPlaylistObject,
                "next_path": "playlists.next",
                "item_path": "playlists.items",
            },
        }

        if search_type not in result_type_map:
            raise ValueError(f"Invalid search_type: {search_type}")

        result_cls: Type = result_type_map[search_type]["obj"]

        if max_items is None:
            return self.request_manager._fetch_from_api(
                endpoint,
                params,
                lambda item: result_cls(**item),
                next_path=result_type_map[search_type]["next_path"],
                item_path=result_type_map[search_type]["item_path"],
            )
        else:
            return self.request_manager._fetch_limited_from_api(
                endpoint,
                params,
                lambda item: result_cls(**item),
                max_items,
                next_path=result_type_map[search_type]["next_path"],
                item_path=result_type_map[search_type]["item_path"],
            )

    # [Not tested]
    def shuffle_playlist(self, playlist_id: str):
        # Get all the tracks in the playlist
        all_tracks = self.get_all_playlist_tracks(playlist_id)

        # Extract URIs from the tracks
        track_uris = [track.uri for track in all_tracks]

        # Get the total number of tracks
        total_tracks = len(track_uris)

        # Create a list of positions
        positions = list(range(total_tracks))

        # Shuffle the positions
        random.shuffle(positions)

        # Reorder the tracks one by one to the shuffled positions
        for i in range(total_tracks):
            # The position of the item to be reordered
            range_start = i

            # The position where the item should be inserted
            insert_before = positions[i]

            # The amount of items to be reordered (only one item in this case)
            range_length = 1

            # Send the request
            response = self.request_manager.put(
                f"/v1/playlists/{playlist_id}/tracks",
                json=dict(
                    range_start=range_start,
                    insert_before=insert_before,
                    range_length=range_length,
                ),
            )

            # Handle the response here (e.g., check for success, handle errors)
            print(response)

        return f"Shuffled playlist {playlist_id} successfully"

    # [Not tested]
    def remove_duplicate_tracks(self, playlist_id: str):
        # Create a dictionary to track unique tracks
        unique_tracks = defaultdict(list)

        # Get all the tracks in the playlist
        all_tracks = list(self.get_all_playlist_tracks(playlist_id))

        # Identify unique tracks and their positions in the playlist
        for idx, track in enumerate(all_tracks):
            key = (
                track.track.name,
                tuple(artist.name for artist in track.track.artists),
            )
            unique_tracks[key].append(idx)

        # Identify the duplicate tracks to remove (keep the first occurrence of each track)
        tracks_to_remove = [
            idx for indices in unique_tracks.values() for idx in indices[1:]
        ]

        # Create a list of dictionaries with each track URI and position
        track_dicts = [{"uri": all_tracks[idx].uri} for idx in tracks_to_remove]

        print(f"Total tracks to remove: {len(tracks_to_remove)}")

        # Divide the track dictionaries into batches of 100
        batch_size = 100
        for i in range(0, len(track_dicts), batch_size):
            batch = track_dicts[i : i + batch_size]

            # Create the JSON payload
            data = {"tracks": batch}

            # Send the request to remove the duplicate tracks
            self.request_manager.delete(
                f"/v1/playlists/{playlist_id}/tracks", json=data
            )

        return f"Removed duplicate tracks from playlist {playlist_id} successfully"

    # [Not tested]
    def get_recommendations(
        self,
        seed_artists: Optional[List[str]] = None,
        seed_genres: Optional[List[str]] = None,
        seed_tracks: Optional[List[str]] = None,
        min_acousticness: Optional[float] = None,
        max_acousticness: Optional[float] = None,
        target_acousticness: Optional[float] = None,
        min_danceability: Optional[float] = None,
        max_danceability: Optional[float] = None,
        target_danceability: Optional[float] = None,
        min_duration_ms: Optional[int] = None,
        max_duration_ms: Optional[int] = None,
        target_duration_ms: Optional[int] = None,
        min_energy: Optional[float] = None,
        max_energy: Optional[float] = None,
        target_energy: Optional[float] = None,
        min_instrumentalness: Optional[float] = None,
        max_instrumentalness: Optional[float] = None,
        target_instrumentalness: Optional[float] = None,
        min_key: Optional[int] = None,
        max_key: Optional[int] = None,
        target_key: Optional[int] = None,
        min_liveness: Optional[float] = None,
        max_liveness: Optional[float] = None,
        target_liveness: Optional[float] = None,
        min_loudness: Optional[float] = None,
        max_loudness: Optional[float] = None,
        target_loudness: Optional[float] = None,
        min_mode: Optional[int] = None,
        max_mode: Optional[int] = None,
        target_mode: Optional[int] = None,
        min_popularity: Optional[int] = None,
        max_popularity: Optional[int] = None,
        target_popularity: Optional[int] = None,
        min_speechiness: Optional[float] = None,
        max_speechiness: Optional[float] = None,
        target_speechiness: Optional[float] = None,
        min_tempo: Optional[float] = None,
        max_tempo: Optional[float] = None,
        target_tempo: Optional[float] = None,
        min_time_signature: Optional[int] = None,
        max_time_signature: Optional[int] = None,
        target_time_signature: Optional[int] = None,
        limit: Optional[int] = 20,
    ) -> dict:
        # Ensure at least one seed parameter is provided
        if not seed_artists and not seed_genres and not seed_tracks:
            raise ValueError(
                "At least one seed parameter (seed_artists, seed_genres, seed_tracks) must be provided."
            )

        # Construct query parameters
        params = {
            "limit": limit,
            "seed_artists": ",".join(seed_artists) if seed_artists else None,
            "seed_genres": ",".join(seed_genres) if seed_genres else None,
            "seed_tracks": ",".join(seed_tracks) if seed_tracks else None,
            "min_acousticness": min_acousticness,
            "max_acousticness": max_acousticness,
            "target_acousticness": target_acousticness,
            "min_danceability": min_danceability,
            "max_danceability": max_danceability,
            "target_danceability": target_danceability,
            "min_duration_ms": min_duration_ms,
            "max_duration_ms": max_duration_ms,
            "target_duration_ms": target_duration_ms,
            "min_energy": min_energy,
            "max_energy": max_energy,
            "target_energy": target_energy,
            "min_instrumentalness": min_instrumentalness,
            "max_instrumentalness": max_instrumentalness,
            "target_instrumentalness": target_instrumentalness,
            "min_key": min_key,
            "max_key": max_key,
            "target_key": target_key,
            "min_liveness": min_liveness,
            "max_liveness": max_liveness,
            "target_liveness": target_liveness,
            "min_loudness": min_loudness,
            "max_loudness": max_loudness,
            "target_loudness": target_loudness,
            "min_mode": min_mode,
            "max_mode": max_mode,
            "target_mode": target_mode,
            "min_popularity": min_popularity,
            "max_popularity": max_popularity,
            "target_popularity": target_popularity,
            "min_speechiness": min_speechiness,
            "max_speechiness": max_speechiness,
            "target_speechiness": target_speechiness,
            "min_tempo": min_tempo,
            "max_tempo": max_tempo,
            "target_tempo": target_tempo,
            "min_time_signature": min_time_signature,
            "max_time_signature": max_time_signature,
            "target_time_signature": target_time_signature,
        }

        params = {key: value for key, value in params.items() if value is not None}

        # Make the GET request and return the result
        response = self.get("/v1/recommendations", params=params)
        return Recommendations(**response)

    # [Not tested]
    def remove_unplayable_tracks(self, playlist_id: str):
        not_playable_tracks = []
        for track in self.get_all_playlist_tracks(playlist_id):
            if not track.track.is_playable:
                not_playable_tracks.append(track.track.uri)

        # Remove tracks 100 at a time
        for i in range(0, len(not_playable_tracks), 100):
            tracks_to_remove = not_playable_tracks[i : i + 100]
            self.remove_playlist_items(playlist_id, tracks_to_remove)

        return True
