from abc import ABC, abstractmethod
from contextvars import ContextVar
from typing import ClassVar, Self


class StackFrame[T]:
    value: T
    parent: StackFrame[T] | None

    __slots__ = ("parent", "value")

    def __init__(self, value: T, parent: StackFrame[T] | None = None) -> None:
        self.value = value
        self.parent = parent


class ContextStack(ABC):
    __context_frame__: ClassVar[ContextVar[StackFrame[Self] | None]]

    __slots__ = ()

    def __init_subclass__(cls, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        if "__context_frame__" not in cls.__dict__:
            cls.__context_frame__ = ContextVar(
                f"{cls.__name__}.__context_frame__",
                default=None,
            )

    @classmethod
    def current(cls) -> Self | None:
        frame = cls.__context_frame__.get()
        return frame.value if frame else None

    @abstractmethod
    def __enter__(self) -> object:
        current_frame = self.__context_frame__.get()
        new_frame = StackFrame(self, current_frame)
        self.__context_frame__.set(new_frame)
        return self

    @abstractmethod
    def __exit__(self, exc_type: object, exc_val: object, exc_tb: object) -> object:
        current_frame = self.__context_frame__.get()

        if current_frame is None:
            msg = "Context stack is empty"
            raise RuntimeError(msg)

        if current_frame.value is not self:
            msg = "Context stack is corrupted"
            raise RuntimeError(msg)

        self.__context_frame__.set(current_frame.parent)
        return None


class ReentryCounter(ABC):
    __context_reentry_count__: ContextVar[int]

    __slots__ = ("__context_reentry_count__",)

    def __init_subclass__(cls, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        original_init = cls.__dict__.get("__init__")

        def _init(self: Self, *args: object, **kwargs: object) -> None:
            if "__context_reentry_count__" not in self.__dict__:
                self.__context_reentry_count__ = ContextVar(
                    f"{self.__class__.__name__}.__context_reentry_count__",
                    default=0,
                )
            if original_init is not None:
                original_init(self, *args, **kwargs)
            else:
                super(cls, self).__init__(*args, **kwargs)

        cls.__init__ = _init

    @property
    def reentry_count(self) -> int:
        return self.__context_reentry_count__.get()

    @abstractmethod
    def __enter__(self) -> object:
        self.__context_reentry_count__.set(self.__context_reentry_count__.get() + 1)
        return self

    @abstractmethod
    def __exit__(self, exc_type: object, exc_val: object, exc_tb: object) -> object:
        self.__context_reentry_count__.set(self.__context_reentry_count__.get() - 1)
        return None


class ReentryGuard(ReentryCounter, ABC):
    __context_max_reentries__: ClassVar[int]

    def __init_subclass__(cls, max_reentries: int, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        if "__context_max_reentries__" not in cls.__dict__:
            cls.__context_max_reentries__ = max_reentries

    @abstractmethod
    def __enter__(self) -> object:
        if self.reentry_count >= self.__context_max_reentries__:
            msg = f"Maximum reentries of {self.__context_max_reentries__} exceeded"
            raise RuntimeError(msg)
        return super().__enter__()


class EntryCounter(ABC):
    __context_entry_count__: ClassVar[ContextVar[int]]

    __slots__ = ()

    def __init_subclass__(cls, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        if "__context_entry_count__" not in cls.__dict__:
            cls.__context_entry_count__ = ContextVar(
                f"{cls.__name__}.__context_entry_count__",
                default=0,
            )

    @property
    def entry_count(self) -> int:
        return self.__context_entry_count__.get()

    @abstractmethod
    def __enter__(self) -> object:
        self.__context_entry_count__.set(self.__context_entry_count__.get() + 1)
        return self

    @abstractmethod
    def __exit__(self, exc_type: object, exc_val: object, exc_tb: object) -> object:
        self.__context_entry_count__.set(self.__context_entry_count__.get() - 1)
        return None


class EntryGuard(EntryCounter, ABC):
    __context_max_entries__: ClassVar[int]

    def __init_subclass__(cls, max_entries: int, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        if "__context_max_entries__" not in cls.__dict__:
            cls.__context_max_entries__ = max_entries

    @abstractmethod
    def __enter__(self) -> object:
        if self.entry_count >= self.__context_max_entries__:
            msg = f"Maximum entries of {self.__context_max_entries__} exceeded"
            raise RuntimeError(msg)
        return super().__enter__()
