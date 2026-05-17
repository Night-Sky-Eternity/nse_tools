import functools
import inspect
from typing import TYPE_CHECKING, Any, Concatenate, Final

if TYPE_CHECKING:
    from collections.abc import Callable, Hashable, Iterable

    from type_checker.nse_pytoolkit.aliases import NotEmptyTuple

    from . import Trackable
    from .data_base import DataBase


class Tracker[T]:
    dependencies: Final[set[Trackable]]
    function: Final[Callable[[DataBase], T]]
    cache_key: Final[Hashable]

    __slots__ = ("cache_key", "dependencies", "function")

    def __init__(
        self,
        function: Callable[[DataBase], T],
        dependencies: Iterable[Trackable],
        cache_key: Hashable | None = None,
    ) -> None:
        self.function = function
        self.dependencies = set(dependencies)
        self.cache_key = cache_key or self

    def get(self, db: DataBase) -> T:
        return db.get_tracker(self)

    def __call__(self, db: DataBase) -> T:
        return self.get(db)

    def __getitem__(self, key: DataBase) -> T:
        return self.get(key)

    @classmethod
    def changed(cls, old: T, new: T) -> bool:
        return old != new


class tracks:  # noqa: N801
    def __init__(
        self,
        *dependencies: *NotEmptyTuple[Trackable],
        tracker: type[Tracker[Any]] = Tracker,
    ) -> None:
        self.dependencies = dependencies
        self.tracker = tracker

    def bound[R](self, func: Callable[[DataBase], R]) -> Tracker[R]:
        return self.tracker(func, self.dependencies)

    def __call__[**P, R](
        self,
        func: Callable[Concatenate[DataBase, P], R],
    ) -> ArgTrackerFactory[P, R]:
        return ArgTrackerFactory(self.dependencies, func, tracker=self.tracker)


class ArgTrackerFactory[**P, R]:
    def __init__(
        self,
        dependencies: Iterable[Trackable],
        func: Callable[Concatenate[DataBase, P], R],
        *,
        tracker: type[Tracker[Any]] = Tracker,
    ) -> None:
        self.dependencies = dependencies
        self.func = func
        self.tracker = tracker

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> Tracker[R]:
        @functools.wraps(self.func)
        def inner(db: DataBase) -> R:
            return self.func(db, *args, **kwargs)

        return self.tracker(inner, self.dependencies, self.cache_key(*args, **kwargs))

    def cache_key(self, *args: P.args, **kwargs: P.kwargs) -> Hashable:
        bound = inspect.signature(self.func).bind(None, *args, **kwargs)
        bound.apply_defaults()
        return self.func, *bound.args[1:], *bound.kwargs.items()
