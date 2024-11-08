from typing import Callable, Type, TypeVar


T = TypeVar("T")


def nullable_parser(fromType: Callable[[str], T]) -> Callable[[str], T | None]:
    """
    Creates a typed parser that treats empty strings as `None`.

    Args:
        fromType:
            The type to parse.

    Returns:
        The typed nullable parser.
    """

    def parse_nullable(value: str) -> T | None:
        if value:
            return fromType(value)
        return None

    return parse_nullable
