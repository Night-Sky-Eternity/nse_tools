from collections.abc import Iterable

from .protocols import SupportsKeysAndGetitem

__all__ = ["MapLike", "MapLikeDefault", "NotEmptyTuple"]

type MapLike[K, V] = SupportsKeysAndGetitem[K, V] | Iterable[tuple[K, V]]
type MapLikeDefault[K, V] = SupportsKeysAndGetitem[K, V] | Iterable[tuple[K, V] | K]
type NotEmptyTuple[T] = tuple[T, *tuple[T, ...]]
