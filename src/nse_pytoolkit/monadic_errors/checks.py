# src/monadic_errors/checks.py
from typing import TYPE_CHECKING, Any, TypeIs, overload

from .classes import Err, Ok, Result

if TYPE_CHECKING:
    from nse_pytoolkit.aliases import NotEmptyTuple


@overload
def is_error[O, E: BaseException](
    res: Result[O, Any],
    /,
    *exc: *NotEmptyTuple[type[E]],
) -> TypeIs[Err[E]]: ...


@overload
def is_error[O, E: BaseException](
    res: Result[O, E],
    /,
) -> TypeIs[Err[E]]: ...


def is_error[O, E: BaseException](
    res: Result[O, E],
    /,
    *exc: type[E],
) -> TypeIs[Err[E]]:
    if not exc:
        return isinstance(res, Err)

    if is_error(res):
        return isinstance(res.error, exc)

    return False


@overload
def is_okay[O, E: BaseException](
    res: Result[Any, E],
    /,
    *val: *NotEmptyTuple[type[O]],
) -> TypeIs[Ok[O]]: ...


@overload
def is_okay[O, E: BaseException](
    res: Result[O, E],
    /,
) -> TypeIs[Ok[O]]: ...


def is_okay[O, E: BaseException](
    res: Result[O, E],
    /,
    *val: type[O],
) -> TypeIs[Ok[O]]:
    if not val:
        return isinstance(res, Ok)

    if is_okay(res):
        return isinstance(res.value, val)

    return False
