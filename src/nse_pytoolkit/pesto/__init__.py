from typing import Any

from .data_base import DataBase
from .inputs import Input
from .trackers import ArgTrackerFactory, Tracker, tracks

type Trackable[T = Any] = Tracker[T] | Input[T]

__all__ = ("ArgTrackerFactory", "DataBase", "Input", "Trackable", "Tracker", "tracks")
