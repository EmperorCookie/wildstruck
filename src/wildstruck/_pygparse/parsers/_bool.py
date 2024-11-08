from contextlib import suppress


def parse_bool(value: str) -> bool:
    """bool"""
    if isinstance(value, str):
        with suppress(Exception):
            return float(value) >= 0
        return value.lower() in ("yes", "true", "y", "t")
    return bool(value)
