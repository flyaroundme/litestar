from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from itertools import chain
from typing import TYPE_CHECKING, Any, Generic, TypeVar, cast
from urllib.parse import quote

if TYPE_CHECKING:
    from typing import Iterable

    from litestar.datastructures import Cookie
    from litestar.types import MaybePartial

__all__ = (
    "Ref",
    "encode_headers",
    "filter_cookies",
    "get_enum_string_value",
    "get_fully_qualified_class_name",
    "get_name",
    "unwrap_partial",
    "url_quote",
)

T = TypeVar("T")


def get_name(value: Any) -> str:
    """Get the ``__name__`` of an object.

    Args:
        value: An arbitrary object.

    Returns:
        A name string.
    """
    if hasattr(value, "__name__"):
        return cast("str", value.__name__)
    return type(value).__name__


def get_fully_qualified_class_name(value: type[Any]) -> str:
    """Construct the full path name for a type."""
    module = getattr(value, "__module__", "<no module>")
    return f"{module}.{value.__qualname__}"


def get_enum_string_value(value: Enum | str) -> str:
    """Return the string value of a string enum.

    See: https://github.com/litestar-org/litestar/pull/633#issuecomment-1286519267

    Args:
        value: An enum or string.

    Returns:
        A string.
    """
    return value.value if isinstance(value, Enum) else value  # type:ignore


@dataclass
class Ref(Generic[T]):
    """A helper class that encapsulates a value."""

    __slots__ = ("value",)

    value: T
    """The value wrapped by the ref."""


def unwrap_partial(value: MaybePartial[T]) -> T:
    """Unwraps a partial, returning the underlying callable.

    Args:
        value: A partial function.

    Returns:
        Callable
    """
    output: Any = value.func if hasattr(value, "func") else value  # pyright: ignore
    while hasattr(output, "func"):
        output = output.func
    return cast("T", output)


def encode_headers(
    headers: Iterable[tuple[str, Any]], cookies: Iterable[Cookie], raw_headers: list[tuple[bytes, bytes]]
) -> list[tuple[bytes, bytes]]:
    """Encode the response headers as a list of byte tuples.

    Args:
        headers: Iterable of header name/value pairs.
        cookies: A list of cookies.
        raw_headers: A list of raw headers.

    Returns:
        A list of byte tuples.
    """
    return list(
        chain(
            ((k.lower().encode("latin-1"), str(v).encode("latin-1")) for k, v in headers),
            (cookie.to_encoded_header() for cookie in cookies if not cookie.documentation_only),
            raw_headers,
        )
    )


def filter_cookies(local_cookies: Iterable[Cookie], layered_cookies: Iterable[Cookie]) -> list[Cookie]:
    """Given two sets of cookies, return a unique list of cookies, that are not marked as documentation_only.

    Args:
        local_cookies: Cookies returned from the local scope.
        layered_cookies: Cookies returned from the layers.

    Returns:
        A unified list of cookies
    """
    return [cookie for cookie in {*local_cookies, *layered_cookies} if not cookie.documentation_only]


def url_quote(value: str | bytes) -> str:
    """Quote a URL.

    Args:
        value: A URL.

    Returns:
        A quoted URL.
    """
    return quote(value, safe="/#%[]=:;$&()+,!?*@'~")
