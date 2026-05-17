# type_checker/pesto/inputs.py

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .data_base import DataBase


class Input[T]:
    __slots__ = ()

    def get(self, db: DataBase) -> T:
        return db.get_input(self)

    def set(self, db: DataBase, value: T) -> None:
        db.set_input(self, value)

    def __call__(self, db: DataBase) -> T:
        return self.get(db)

    def __getitem__(self, key: DataBase) -> T:
        return self.get(key)

    def __setitem__(self, key: DataBase, value: T) -> None:
        self.set(key, value)
