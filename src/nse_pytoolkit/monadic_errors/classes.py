# src/monadic_errors/classes.py
from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Concatenate, Never, Protocol

if TYPE_CHECKING:
    from collections.abc import Callable


class Result[O, E: BaseException](Protocol):
    def bind[U, F: BaseException, **P](
        self,
        f: Callable[Concatenate[O, P], Result[U, F]],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> Result[U, E | F]: ... # rust: and_then

    def bind_err[U, F: BaseException, **P](
        self,
        f: Callable[Concatenate[E, P], Result[U, F]],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> Result[U | O, F]: ... # rust: or_else

    def map[U, **P](
        self,
        f: Callable[Concatenate[O, P], U],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> Result[U, E]: ...

    def map_err[F: BaseException, **P](
        self,
        f: Callable[Concatenate[E, P], F],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> Result[O, F]: ...

    def unwrap(self) -> O: ...

    def unwrap_err(self) -> E: ...

    def unwrap_or[D](self, default: D) -> O | D: ...

    def unwrap_err_or[D](self, default: D) -> D | E: ...

    def unwrap_or_else[D, **P](
        self,
        default_factory: Callable[Concatenate[E, P], D],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> O | D: ...

    def unwrap_err_or_else[D, **P](
        self,
        default_factory: Callable[Concatenate[O, P], D],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> D | E: ...


@dataclass(slots=True, frozen=True)
class Ok[O](Result[O, Never]):
    value: O

    def bind[U, F: BaseException, **P](
        self,
        f: Callable[Concatenate[O, P], Result[U, F]],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> Result[U, F]:
        return f(self.value, *args, **kwargs)

    def bind_err[U, F: BaseException, **P](
        self,
        f: Callable[Concatenate[Never, P], Result[U, F]],  # noqa: ARG002
        *args: P.args,  # noqa: ARG002
        **kwargs: P.kwargs,  # noqa: ARG002
    ) -> Ok[O]:
        return self

    def map[U, **P](
        self,
        f: Callable[Concatenate[O, P], U],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> Ok[U]:
        return Ok(f(self.value, *args, **kwargs))

    def map_err[F: BaseException, **P](
        self,
        f: Callable[Concatenate[Never, P], F],  # noqa: ARG002
        *args: P.args,  # noqa: ARG002
        **kwargs: P.kwargs,  # noqa: ARG002
    ) -> Ok[O]:
        return self

    def unwrap(self) -> O:
        return self.value

    def unwrap_err(self) -> Never:
        msg = "called unwrap_err() on Ok"
        raise UnwrapError(msg)

    def unwrap_or(self, default: object) -> O:  # noqa: ARG002
        return self.value

    def unwrap_err_or[D](self, default: D) -> D:
        return default

    def unwrap_or_else[D, **P](
        self,
        default_factory: Callable[Concatenate[Never, P], Any],  # noqa: ARG002
        *args: P.args,  # noqa: ARG002
        **kwargs: P.kwargs,  # noqa: ARG002
    ) -> O:
        return self.value

    def unwrap_err_or_else[D, **P](
        self,
        default_factory: Callable[Concatenate[O, P], D],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> D:
        return default_factory(self.value, *args, **kwargs)


@dataclass(slots=True, frozen=True)
class Err[E: BaseException](Result[Never, E]):
    error: E

    def bind[U, F: BaseException, **P](
        self,
        f: Callable[Concatenate[Never, P], Result[U, F]],  # noqa: ARG002
        *args: P.args,  # noqa: ARG002
        **kwargs: P.kwargs,  # noqa: ARG002
    ) -> Err[E]:
        return self

    def bind_err[U, F: BaseException, **P](
        self,
        f: Callable[Concatenate[E, P], Result[U, F]],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> Result[U, F]:
        return f(self.error, *args, **kwargs)

    def map[U, **P](
        self,
        f: Callable[Concatenate[Never, P], U],  # noqa: ARG002
        *args: P.args,  # noqa: ARG002
        **kwargs: P.kwargs,  # noqa: ARG002
    ) -> Err[E]:
        return self

    def map_err[F: BaseException, **P](
        self,
        f: Callable[Concatenate[E, P], F],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> Err[F]:
        return Err(f(self.error, *args, **kwargs))

    def unwrap(self) -> Never:
        msg = "called unwrap() on Err"
        raise UnwrapError(msg) from self.error

    def unwrap_err(self) -> E:
        return self.error

    def unwrap_or[D](self, default: D) -> D:
        return default

    def unwrap_err_or(self, default: object) -> E:  # noqa: ARG002
        return self.error

    def unwrap_or_else[D, **P](
        self,
        default_factory: Callable[Concatenate[E, P], D],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> D:
        return default_factory(self.error, *args, **kwargs)

    def unwrap_err_or_else[D, **P](
        self,
        default_factory: Callable[Concatenate[Never, P], Any],  # noqa: ARG002
        *args: P.args,  # noqa: ARG002
        **kwargs: P.kwargs,  # noqa: ARG002
    ) -> E:
        return self.error


class UnwrapError(Exception):
    pass
