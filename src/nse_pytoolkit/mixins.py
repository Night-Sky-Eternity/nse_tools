from abc import ABC, abstractmethod
from collections.abc import Iterator, KeysView, Mapping

from nse_pytoolkit.protocols import SupportsKeysAndGetitem

__all__ = ["MappingMixin"]


class MappingMixin[K, V](SupportsKeysAndGetitem[K, V], Mapping[K, V], ABC):
    @abstractmethod
    def keys(self) -> KeysView[K]: ...

    @abstractmethod
    def __getitem__(self, key: K, /) -> V: ...

    def __iter__(self) -> Iterator[K]:
        return iter(self.keys())

    def __len__(self) -> int:
        return len(self.keys())
