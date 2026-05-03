import threading
from abc import ABC, ABCMeta
from collections.abc import Iterator, Sized
from contextvars import ContextVar
from typing import TYPE_CHECKING, ClassVar, Literal, Self

if TYPE_CHECKING:
    from types import TracebackType

__all__ = [
    "ContextCounter",
    "ContextStack",
    "LimitedContextStack",
    "LimitedContextStackMeta",
]


class ContextCounter(Iterator[int], Sized):
    """Return an independent thread-safe counter. Call next() on it to get sequential IDs."""

    __slots__ = ("_count", "_lock")

    def __init__(self) -> None:
        self._count = 0
        self._lock = threading.Lock()

    def __iter__(self) -> Self:
        return self

    def __len__(self) -> int:
        with self._lock:
            return self._count

    def __next__(self) -> int:
        with self._lock:
            self._count += 1
            return self._count


class ContextStack(ABC):
    __context_stack__: ClassVar[ContextVar[list[Self] | None]]

    __slots__ = ()

    def __init_subclass__(cls, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        cls.__context_stack__ = ContextVar(f"{cls.__name__}_stack", default=None)

    @classmethod
    def current(cls) -> Self | None:
        stack = cls.__context_stack__.get()
        return stack[-1] if stack else None

    def __enter__(self) -> Self:
        stack: list[Self] | None = self.__context_stack__.get()
        if stack is None:
            stack = []
            self.__context_stack__.set(stack)
        stack.append(self)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None = None,
        exc_value: BaseException | None = None,
        traceback: TracebackType | None = None,
    ) -> Literal[False]:

        stack = self.__context_stack__.get()
        if stack is None:
            msg = f"{type(self).__name__} stack is None on __exit__"
            raise RuntimeError(msg)
        stack.pop()
        return False


class LimitedContextStackMeta(ABCMeta):
    __context_max_entries__: ClassVar[int]
    __context_semaphore__: threading.Semaphore

    def __call__[T: LimitedContextStackMeta](
        cls: type[T],
        *args: object,
        **kwargs: object,
    ) -> T:
        obj: T = super().__call__(*args, **kwargs)
        obj.__context_semaphore__ = threading.Semaphore(cls.__context_max_entries__)
        return obj


class LimitedContextStack(ContextStack, ABC, metaclass=LimitedContextStackMeta):
    __slots__ = ("__context_semaphore__",)

    def __init_subclass__(cls, *, max_entries: int = 1, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        cls.__context_max_entries__ = max_entries

    def __enter__(self) -> Self:
        if not self.__context_semaphore__.acquire(blocking=False):
            msg = f"Cannot enter '{type(self).__name__}' context more than '{self.__context_max_entries__}'"
            raise RuntimeError(msg)
        try:
            return super().__enter__()
        except:
            self.__context_semaphore__.release()
            raise

    def __exit__(
        self,
        exc_type: type[BaseException] | None = None,
        exc_value: BaseException | None = None,
        traceback: TracebackType | None = None,
    ) -> Literal[False]:
        result = super().__exit__(exc_type, exc_value, traceback)
        self.__context_semaphore__.release()
        return result
