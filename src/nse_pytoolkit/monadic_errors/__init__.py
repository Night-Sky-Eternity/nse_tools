from .checks import is_error, is_okay
from .classes import Err, Ok, Result
from .decorator import catches

__all__ = ["Err", "Ok", "Result", "catches", "is_error", "is_okay"]
