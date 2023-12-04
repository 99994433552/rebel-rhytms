class SpotifyClientException(Exception):
    """Base exception class for the SpotifyClient."""

    pass


class ResourceNotFoundException(SpotifyClientException):
    """Raised when a requested resource is not found."""

    pass


class UnauthorizedException(SpotifyClientException):
    """Raised when authentication is required but has failed or not been provided."""

    pass


class ForbiddenException(SpotifyClientException):
    """Raised when the client does not have permission to access the requested resource."""

    pass


class InternalServerErrorException(SpotifyClientException):
    """Raised when the server encounters an internal error."""

    pass


class RateLimitException(SpotifyClientException):
    pass


class BadRequestException(SpotifyClientException):
    pass
