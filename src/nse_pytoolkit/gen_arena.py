from dataclasses import dataclass, field

from .sentinels import FREE, MISSING, FreeType

__all__ = [
    "ArenaError",
    "ArenaIndexHandleError",
    "FreeSlotError",
    "GenArena",
    "GenerationMismatchHandleError",
    "Handle",
]

type Handle = tuple[int, int]


class ArenaError(Exception):
    """Base class for arena handle violations."""


class ArenaIndexHandleError(ArenaError):
    """Handle refers to an incorrect index."""


class GenerationMismatchHandleError(ArenaError):
    """Handle refers to an outdated generation."""


class FreeSlotError(ArenaError):
    """Handle refers to a free slot."""


@dataclass(slots=True)
class GenArena[T]:
    """Generational arena storing values with reusable slots.

    Each inserted value is assigned a stable index and generation.
    When a slot is reused after being freed, its generation increments
    so stale handles can be detected.

    Private Attributes:
        _values (list[T | FreeType]): Storage for values or free markers.
        _gens (list[int]): Generation counter for each slot.
        _free (list[int]): Stack of reusable free slot indices.
    """

    _values: list[T | FreeType] = field(default_factory=list, repr=False)
    _gens: list[int] = field(default_factory=list, repr=False)
    _free: list[int] = field(default_factory=list, repr=False)

    # ---------------------------------------------------------

    def insert(self, value: T) -> Handle:
        """Insert a value and return its handle.

        If a previously freed slot is reused, its generation is
        incremented before assignment so prior handles become invalid.

        Args:
            value: Value to store in the arena.

        Returns:
            (index, generation) handle for later access.
        """

        if self._free:
            index = self._free.pop()

            # Generation bump happens HERE (on reuse)
            self._gens[index] += 1
            self._values[index] = value
        else:
            index = len(self._values)
            self._values.append(value)
            self._gens.append(0)

        return index, self._gens[index]

    # ---------------------------------------------------------

    def _release(self, index: int) -> None:
        """Invalidate an internal slot.

        Marks slot free and makes it reusable.
        Generation is NOT modified here — it advances only when the
        slot is reused on a future insert.

        Assumes caller already validated handle.
        """

        self._values[index] = FREE
        self._free.append(index)

    # ---------------------------------------------------------

    def get[D](self, index: int, generation: int, /, default: D = MISSING) -> T | D:
        """Retrieve a value from a handle.

        Raises:
            ArenaIndexHandleError: Handle index is incorrect.
            GenerationMismatchError: Handle generation is stale.
            FreeSlotError: Slot is currently unoccupied.

        Returns:
            Stored value, or default if provided.
        """

        if not (0 <= index < len(self._values)):
            if default is MISSING:
                msg = f"Invalid slot index {index}"
                raise ArenaIndexHandleError(msg)
            return default

        if self._gens[index] != generation:
            if default is MISSING:
                msg = (
                    f"Generation mismatch for slot {index}: got {generation}, "
                    f"expected {self._gens[index]}"
                )
                raise GenerationMismatchHandleError(msg)
            return default

        value = self._values[index]

        if value is FREE:
            if default is MISSING:
                msg = f"Slot {(index, generation)} is free"
                raise FreeSlotError(msg)
            return default

        return value

    # ---------------------------------------------------------

    def free(self, index: int, generation: int, /, *, raises: bool = True) -> bool:
        """Release a slot referenced by a handle.

        Args:
            index: Slot index to release.
            generation: Expected generation of the slot.
            raises: Raise on failure instead of returning False.

        Raises:
            ArenaIndexHandleError: Handle index is incorrect.
            GenerationMismatchError: Handle generation is stale.
            DoubleFreeError: Slot has already been freed.

        Returns:
            True if released, False if suppressed failure.
        """

        if not (0 <= index < len(self._values)):
            if raises:
                msg = f"Invalid slot index {index}"
                raise ArenaIndexHandleError(msg)
            return False

        if self._gens[index] != generation:
            if raises:
                msg = (
                    f"Generation mismatch for slot {index}: got {generation}, "
                    f"expected {self._gens[index]}"
                )
                raise GenerationMismatchHandleError(msg)
            return False

        if self._values[index] is FREE:
            if raises:
                msg = f"Slot {(index, generation)} already free"
                raise FreeSlotError(msg)
            return False

        self._release(index)
        return True

    # ---------------------------------------------------------

    def pop[D](self, index: int, generation: int, /, default: D = MISSING) -> T | D:
        """Remove and return the value from a handle.

        Raises:
            ArenaIndexHandleError: Handle index is incorrect.
            GenerationMismatchError: Handle generation is stale.
            DoubleFreeError: Slot is already free.

        Returns:
            Removed value, or default if provided.
        """

        if not (0 <= index < len(self._values)):
            if default is MISSING:
                msg = f"Invalid slot index {index}"
                raise ArenaIndexHandleError(msg)
            return default

        if self._gens[index] != generation:
            if default is MISSING:
                msg = (
                    f"Generation mismatch for slot {index}: got {generation}, "
                    f"expected {self._gens[index]}"
                )
                raise GenerationMismatchHandleError(msg)
            return default

        value = self._values[index]

        if value is FREE:
            if default is MISSING:
                msg = f"Slot {(index, generation)} already free"
                raise FreeSlotError(msg)
            return default

        self._release(index)
        return value
