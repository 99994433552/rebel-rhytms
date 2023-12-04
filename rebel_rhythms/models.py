from typing import List

from pydantic import BaseModel


class ExternalUrls(BaseModel):
    spotify: str


class Restrictions(BaseModel):
    reason: str


class ImageObject(BaseModel):
    height: int | None = None
    width: int | None = None
    url: str


class CopyrightObject(BaseModel):
    text: str
    type: str


class ExternalIds(BaseModel):
    isrc: str | None = None
    ean: str | None = None
    upc: str | None = None


class Followers(BaseModel):
    href: str | None = None
    total: int


class LinkedFrom(BaseModel):
    external_urls: ExternalUrls
    href: str
    id: str
    type: str
    uri: str


class SimplifiedArtistObject(BaseModel):
    external_urls: ExternalUrls
    href: str
    id: str
    name: str
    type: str
    uri: str


class ArtistObject(BaseModel):
    external_urls: ExternalUrls
    href: str
    id: str
    name: str
    type: str
    uri: str
    followers: Followers | None = None
    genres: List[str] | None = None
    images: List[ImageObject] | None = None
    popularity: int | None = None


class SimplifiedTrackObject(BaseModel):
    artists: List[SimplifiedArtistObject]
    available_markets: List[str] | None = None
    disc_number: int
    duration_ms: int
    explicit: bool
    external_urls: ExternalUrls
    href: str
    id: str
    is_playable: bool | None = None
    linked_from: LinkedFrom | None = None
    restrictions: Restrictions | None = None
    name: str
    preview_url: str | None = None
    track_number: int
    type: str
    uri: str
    is_local: bool


class Tracks(BaseModel):
    href: str
    limit: int
    next: str | None = None
    offset: int
    previous: str | None = None
    total: int
    items: List[SimplifiedTrackObject]


class AlbumObject(BaseModel):
    album_type: str
    total_tracks: int
    available_markets: List[str] | None = None
    external_urls: ExternalUrls
    href: str
    id: str
    images: List[ImageObject]
    name: str
    release_date: str
    release_date_precision: str
    restrictions: Restrictions | None = None
    type: str
    uri: str
    copyrights: List[CopyrightObject] | None = None
    external_ids: ExternalIds | None = None
    genres: List[str] | None = None
    label: str | None = None
    popularity: int | None = None
    artists: List[ArtistObject]
    tracks: Tracks | None = None


class SimplifiedAlbumObject(BaseModel):
    album_type: str
    total_tracks: int
    available_markets: List[str] | None = None
    external_urls: ExternalUrls
    href: str
    id: str
    images: List[ImageObject]
    name: str
    release_date: str
    release_date_precision: str
    restrictions: Restrictions | None = None
    type: str
    uri: str
    copyrights: List[CopyrightObject] | None = None
    external_ids: ExternalIds | None = None
    genres: List[str] | None = None
    label: str | None = None
    popularity: int | None = None
    album_group: str | None = None
    artists: List[SimplifiedArtistObject]


class SavedAlbumObject(BaseModel):
    added_at: str
    album: AlbumObject


class TrackAlbum(BaseModel):
    album_type: str
    total_tracks: int
    available_markets: List[str] | None = None
    extenal_urls: ExternalUrls | None = None
    href: str
    id: str
    images: List[ImageObject]
    name: str
    release_date: str
    release_date_precision: str
    restrictions: Restrictions | None = None
    type: str
    uri: str
    copyrights: List[CopyrightObject] | None = None
    external_ids: ExternalIds | None = None
    genres: List[str] | None = None
    label: str | None = None
    popularity: int | None = None
    album_group: str | None = None
    artists: List[SimplifiedArtistObject]


class Track(BaseModel):
    album: TrackAlbum
    artists: List[ArtistObject]
    available_markets: List[str] | None = None
    disc_number: int
    duration_ms: int
    explicit: bool
    external_ids: ExternalIds | None = None
    href: str
    id: str
    is_playable: bool | None = None
    linked_from: LinkedFrom | None = None
    restrictions: Restrictions | None = None
    name: str
    popularity: int | None = None
    preview_url: str | None = None
    track_number: int
    type: str
    uri: str
    is_local: bool


class BrowseCategory(BaseModel):
    href: str
    icons: List[ImageObject]
    id: str
    name: str


class PlaylistOwner(BaseModel):
    external_urls: ExternalUrls
    followers: Followers | None = None
    href: str
    id: str
    type: str
    uri: str
    display_name: str | None = None


class PlaylistTrackAddedBy(BaseModel):
    external_urls: ExternalUrls
    followers: Followers | None = None
    href: str
    id: str
    type: str
    uri: str


class PlaylistTrackObject(BaseModel):
    added_at: str
    added_by: PlaylistTrackAddedBy
    is_local: bool
    track: Track


class PlaylistTracks(BaseModel):
    href: str
    limit: int
    next: str | None = None
    offset: int
    previous: str | None = None
    total: int
    items: List[PlaylistTrackObject]


class Playlist(BaseModel):
    collaborative: bool | None = None
    description: str | None = None
    external_urls: ExternalUrls
    followers: Followers | None = None
    href: str
    id: str
    images: List[ImageObject]
    name: str
    owner: PlaylistOwner
    public: bool | None = None
    snapshot_id: str
    tracks: PlaylistTracks
    type: str
    uri: str


class SimplifiedPlaylistTrack(BaseModel):
    href: str
    total: int


class SimplifiedPlaylistObject(BaseModel):
    collaborative: bool | None = None
    description: str | None = None
    external_urls: ExternalUrls
    followers: Followers | None = None
    href: str
    id: str
    images: List[ImageObject]
    name: str
    owner: PlaylistOwner
    public: bool | None = None
    snapshot_id: str
    tracks: PlaylistTracks
    type: str
    uri: str
    tracks: SimplifiedPlaylistTrack


class SavedTrackObject(BaseModel):
    added_at: str
    track: Track


class AudioFeaturesObject(BaseModel):
    acousticness: float
    analysis_url: str
    danceability: float
    duration_ms: int
    energy: float
    id: str
    instrumentalness: float
    key: int
    liveness: float
    loudness: float
    mode: int
    speechiness: float
    tempo: float
    time_signature: int
    track_href: str
    type: str
    uri: str
    valence: float


class AudioAnalysisBars(BaseModel):
    start: float
    duration: float
    confidence: float


class AudioAnalysisBeats(BaseModel):
    start: float
    duration: float
    confidence: float


class AudioAnalysisSections(BaseModel):
    start: float
    duration: float
    confidence: float
    loudness: float
    tempo: float
    tempo_confidence: float
    key: int
    key_confidence: float
    mode: float
    mode_confidence: float
    time_signature: int
    time_signature_confidence: float


class AudioAnalysisSegments(BaseModel):
    start: float
    duration: float
    confidence: float
    loudness_start: float
    loudness_max: float
    loudness_max_time: float
    loudness_end: float
    pitches: List[float]
    timbre: List[float]


class AudioAnalysisTatums(BaseModel):
    start: float
    duration: float
    confidence: float


class AudioAnalysisMeta(BaseModel):
    analyzer_version: str
    platform: str
    detailed_status: str
    status_code: int
    timestamp: int
    analysis_time: float
    input_process: str


class AudioAnalysisTrack(BaseModel):
    num_samples: int
    duration: float
    sample_md5: str | None = None
    offset_seconds: int
    window_seconds: int
    analysis_sample_rate: int
    analysis_channels: int
    end_of_fade_in: float
    start_of_fade_out: float
    loudness: float
    tempo: float
    tempo_confidence: float
    time_signature: int
    time_signature_confidence: float
    key: int
    key_confidence: float
    mode: int
    mode_confidence: float
    codestring: str
    code_version: float
    echoprintstring: str
    synchstring: str
    synch_version: int
    rhythmstring: str
    rhythm_version: int


class AudioAnalysisObject(BaseModel):
    meta: AudioAnalysisMeta
    track: AudioAnalysisTrack
    bars: List[AudioAnalysisBars]
    beats: List[AudioAnalysisBeats]
    sections: List[AudioAnalysisSections]
    segments: List[AudioAnalysisSegments]
    tatums: List[AudioAnalysisTatums]


class RecommendationSeedObject(BaseModel):
    afterFilteringSize: int
    afterRelinkingSize: int
    href: str
    id: str
    initialPoolSize: int
    type: str


class Recommendations(BaseModel):
    seeds: List[RecommendationSeedObject]
    tracks: List[Track]


class ExplicitContent(BaseModel):
    filter_enabled: bool
    filter_locked: bool


class User(BaseModel):
    display_name: str
    external_urls: ExternalUrls
    followers: Followers
    href: str
    id: str
    images: List[ImageObject]
    type: str
    uri: str


class CurrentUser(BaseModel):
    display_name: str
    external_urls: ExternalUrls
    followers: Followers
    href: str
    id: str
    images: List[ImageObject]
    type: str
    uri: str
    country: str
    email: str | None = None
    explicit_content: ExplicitContent
    product: str
