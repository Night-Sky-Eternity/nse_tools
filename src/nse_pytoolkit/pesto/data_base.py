from typing import TYPE_CHECKING, Any

from .inputs import Input

if TYPE_CHECKING:
    from collections.abc import Hashable

    from . import Trackable
    from .trackers import Tracker


class DataBase:
    dependents: dict[Trackable, set[Tracker[Any]]]
    input_values: dict[Input[Any], Any]
    tracker_cache: dict[Hashable, Any]
    _stale: set[Hashable]

    __slots__ = ("_stale", "dependents", "input_values", "tracker_cache")

    def __init__(self) -> None:
        self.dependents = {}
        self.input_values = {}
        self.tracker_cache = {}
        self._stale = set()

    def get_input[T](self, i: Input[T]) -> T:
        return self.input_values[i]

    def set_input[T](self, i: Input[T], value: T) -> None:
        self.input_values[i] = value
        for dependent in list(self.dependents.get(i, set())):
            self.invalidate(dependent)

    def update_dependencies(self, tracker: Tracker[Any]) -> None:
        for dep in tracker.dependencies:
            self.dependents.setdefault(dep, set()).add(tracker)

    def refresh(self, tracker: Tracker[Any]) -> None:
        key = tracker.cache_key
        is_new = key not in self.tracker_cache
        new_value = tracker.function(self)

        if is_new or tracker.changed(
            self.tracker_cache[key],
            new_value,
        ):
            self.tracker_cache[key] = new_value
        self._stale.discard(key)

    def get_tracker[T](self, tracker: Tracker[T]) -> T:
        key = tracker.cache_key
        is_new = key not in self.tracker_cache
        is_stale = key in self._stale

        if is_new:
            self.update_dependencies(tracker)

        if is_new or is_stale:
            self.refresh(tracker)

        return self.tracker_cache[key]

    def override_tracker[T](self, tracker: Tracker[T], value: T) -> None:
        key = tracker.cache_key
        self.tracker_cache[key] = value
        self._stale.discard(key)
        for dependent in list(self.dependents.get(tracker, set())):
            self.invalidate(dependent)

    def invalidate(self, tracker: Tracker[Any]) -> None:
        key = tracker.cache_key
        if key in self._stale:
            return
        self._stale.add(key)
        for dependent in list(self.dependents.get(tracker, set())):
            self.invalidate(dependent)

    def get[T](self, key: Trackable[T]) -> T:
        if isinstance(key, Input):
            return self.get_input(key)
        return self.get_tracker(key)
