"""
scrapedatshi.exceptions
~~~~~~~~~~~~~~~~~~~~~~~
All exceptions raised by the scrapedatshi SDK.
"""


class ScrapedatshiError(Exception):
    """Base exception for all scrapedatshi SDK errors."""

    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(message={self.message!r}, status_code={self.status_code})"


class AuthError(ScrapedatshiError):
    """Raised when the API key is missing, invalid, or revoked (HTTP 401/403)."""


class InsufficientCreditsError(ScrapedatshiError):
    """
    Raised when the account credit balance is too low to complete the request (HTTP 402).

    Top up your balance at https://scrapedatshi.com/portal/billing.

    Example::

        from scrapedatshi.exceptions import InsufficientCreditsError

        try:
            result = client.pipeline.sync(...)
        except InsufficientCreditsError:
            print("Balance too low — top up at scrapedatshi.com/portal/billing")
    """


class RateLimitError(ScrapedatshiError):
    """Raised when a per-request hard cap or per-minute rate limit is exceeded (HTTP 429)."""


class TierError(ScrapedatshiError):
    """
    Raised when a request is rejected due to account restrictions (HTTP 403).

    .. deprecated::
        ``TierError`` is kept for backward compatibility. New code should catch
        :class:`InsufficientCreditsError` for credit balance issues and
        :class:`AuthError` for permission errors.
    """


class ValidationError(ScrapedatshiError):
    """Raised when the API returns a 422 Unprocessable Entity (bad request payload)."""


class ServerError(ScrapedatshiError):
    """Raised when the API returns a 5xx server error."""


class TimeoutError(ScrapedatshiError):
    """Raised when the request times out."""
