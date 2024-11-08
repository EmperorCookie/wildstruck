# ----------------------------------------------------------------------------------------------
# Copyright (C) Botni.Vision, Inc - Montreal, QC, Canada - All Rights Reserved
# Unauthorized copying, use, or modification to this file via any medium is strictly prohibited.
# This file is private and confidential.
# Contact: dev@botni.vision
# ----------------------------------------------------------------------------------------------


def parse_hex_string(value: str) -> str:
    """hex"""
    try:
        int(value, 16)
    except Exception as exc:
        raise ValueError(f"Invalid hexadecimal string: '{value}'") from exc
    if value[:2].lower() == "0x":
        return value
    return f"0x{value}"
