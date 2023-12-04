from functools import wraps
import inspect
from enum import Enum, auto
import re
from typing import List, Union


class ContentType(Enum):
    TRACK = auto()
    ALBUM = auto()
    PLAYLIST = auto()
    ARTIST = auto()
    USER = auto()


def validate_boolean_param(param: bool, name: str):
    if param is not None and not isinstance(param, bool):
        raise ValueError(f"The '{name}' parameter must be a boolean.")


def validate_playlist_params(public: bool, collaborative: bool):
    if public and collaborative:
        raise ValueError("You can't set both 'public' and 'collaborative' to True.")


def check_list_limit(arg_name, limit):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()

            the_list = bound_args.arguments.get(arg_name, None)
            if the_list and isinstance(the_list, list) and len(the_list) > limit:
                raise ValueError(f"Too many IDs provided. Maximum allowed is {limit}.")

            return func(*args, **kwargs)

        return wrapper

    return decorator


def validate_track_uris(uris: Union[str, List[str]]) -> List[str]:
    pattern = re.compile(r"^spotify:track:[a-zA-Z0-9]{22}$")
    if isinstance(uris, str):
        track_uris_list = [uris]
    else:
        track_uris_list = uris

    for track_uri in track_uris_list:
        if not pattern.match(track_uri):
            raise ValueError(f"Invalid track URI: {track_uri}")

    return track_uris_list


def validate_id_or_url(content_type: ContentType, multiple: bool = False):
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            sig = inspect.signature(func)
            param_names = list(sig.parameters.keys())[1:]  # skip 'self'

            if args:
                ref = args[0]
                rest_args = args[1:]
            else:
                arg_name = param_names[0]  # assuming 'ref' is the first argument after 'self'
                ref = kwargs.pop(arg_name, None)
                rest_args = args

            if ref is None:
                raise TypeError(f"{func.__name__}() missing 1 required positional argument: '{arg_name}'")

            if multiple:
                if isinstance(ref, str):
                    ref = [ref]
                valid_ids = validate_and_extract_ids(ref, content_type=content_type)
            else:
                valid_ids = validate_and_extract_ids([ref], content_type=content_type)[0]

            return func(self, valid_ids, *rest_args, **kwargs)

        return wrapper

    return decorator


def validate_and_extract_ids(url_or_id: Union[str, List[str]], content_type: ContentType) -> List[str]:
    if not url_or_id:
        raise ValueError("ID or URL should not be empty.")

    if isinstance(url_or_id, str):
        return [validate_and_extract_single_id(url_or_id, content_type)]
    elif isinstance(url_or_id, list):
        return [validate_and_extract_single_id(x, content_type) for x in url_or_id]
    else:
        raise ValueError("Invalid type for ID or URL.")


def validate_and_extract_single_id(url_or_id: str, content_type: ContentType) -> str:
    if not isinstance(url_or_id, str):
        raise ValueError(f"Invalid ID or URL: {url_or_id}")

    # Special pattern for ContentType.USER
    if content_type == ContentType.USER:
        pattern = r"https://open\.spotify\.com/user/([a-zA-Z0-9]+)"
    else:
        pattern = rf"https://open\.spotify\.com/{content_type.name.lower()}/([a-zA-Z0-9]+)"

    match = re.match(pattern, url_or_id)
    if match:
        return match.group(1)

    # Additional check for ContentType.USER to accept generic usernames
    if content_type == ContentType.USER and re.match(r"^[a-zA-Z0-9_-]+$", url_or_id):
        return url_or_id

    if re.match(r"^[a-zA-Z0-9]{22}$", url_or_id):
        return url_or_id

    raise ValueError(f"Invalid ID or URL: {url_or_id}")
