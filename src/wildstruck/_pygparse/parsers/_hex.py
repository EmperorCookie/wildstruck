def parse_hex_string(value: str) -> str:
    """hex"""
    try:
        int(value, 16)
    except Exception as exc:
        raise ValueError(f"Invalid hexadecimal string: '{value}'") from exc
    if value[:2].lower() == "0x":
        return value
    return f"0x{value}"
