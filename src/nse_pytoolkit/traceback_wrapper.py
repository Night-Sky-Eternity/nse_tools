import re
import traceback
from typing import TYPE_CHECKING, overload

if TYPE_CHECKING:
    from types import TracebackType

__all__ = ["format_exception", "format_exception_spec"]


@overload
def format_exception(
    exc: type[BaseException] | None,
    /,
    value: BaseException | None = ...,
    tb: TracebackType | None = ...,
    *,
    limit: int | None = None,
    chain: bool = True,
    colorize: bool = False,
) -> list[str]: ...


@overload
def format_exception(
    exc: BaseException,
    /,
    *,
    limit: int | None = None,
    chain: bool = True,
    colorize: bool = False,
) -> list[str]: ...


def format_exception(
    exc: type[BaseException] | BaseException | None,
    /,
    value: BaseException | None = None,
    tb: TracebackType | None = None,
    *,
    limit: int | None = None,
    chain: bool = True,
    colorize: bool = False,
) -> list[str]:
    if isinstance(exc, BaseException):
        return traceback.format_exception(
            exc,
            limit=limit,
            chain=chain,
            **{"colorize": colorize},  # noqa: PIE804
        )
    return traceback.format_exception(
        exc,
        value,
        tb,
        limit=limit,
        chain=chain,
        **{"colorize": colorize},  # noqa: PIE804
    )


def format_exception_spec(format_spec: str) -> tuple[int | None, bool, bool]:
    limit: int | None = None
    chain: bool = True
    colorize: bool = False

    remaining = format_spec

    match = re.match(r"^(\d+)", remaining)
    if match:
        limit = int(match.group(1))
        remaining = remaining[match.end() :]

    for ch in remaining:
        match ch:
            case "c":
                colorize = True
            case "n":
                chain = False
            case "":
                pass
            case _:
                msg = (
                    f"Unknown format flag {ch!r} in format spec {format_spec!r}. "
                    f"Valid flags: 'c' (colorize), 'n' (no chain), optionally preceded by an integer limit."
                )
                raise ValueError(
                    msg,
                )

    return limit, chain, colorize
