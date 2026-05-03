# src/monadic_errors/decorator.py
import functools
from typing import TYPE_CHECKING

from .classes import Err, Ok, Result

if TYPE_CHECKING:
    from collections.abc import Callable


class catches[E: BaseException]:  # noqa: N801
    exceptions: set[type[E]]

    def __init__(self, *exc: type[E]) -> None:
        self.exceptions = set(exc)

    def __call__[**P, O](self, f: Callable[P, O]) -> Callable[P, Result[O, E]]:
        error_tuple = tuple(self.exceptions)
        @functools.wraps(f)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> Result[O, E]:
            try:
                return Ok(f(*args, **kwargs))
            except error_tuple as e:
                return Err(e)

        return wrapper

    @staticmethod
    def add[F: BaseException](*exc: type[F]) -> AddedCatches[F]:
        return AddedCatches(*exc)

class AddedCatches[E: BaseException]:
    exceptions: set[type[E]]

    def __init__(self, *exc: type[E]) -> None:
        self.exceptions = set(exc)

    def __call__[**P, O, F: BaseException](
        self,
        f: Callable[P, Result[O, F]],
    ) -> Callable[P, Result[O, E | F]]:
        error_tuple = tuple(self.exceptions)
        @functools.wraps(f)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> Result[O, E | F]:
            try:
                return f(*args, **kwargs)
            except error_tuple as e:
                return Err(e)

        return wrapper
