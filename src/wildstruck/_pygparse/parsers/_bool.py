# ----------------------------------------------------------------------------------------------
# Copyright (C) Botni.Vision, Inc - Montreal, QC, Canada - All Rights Reserved
# Unauthorized copying, use, or modification to this file via any medium is strictly prohibited.
# This file is private and confidential.
# Contact: dev@botni.vision
# ----------------------------------------------------------------------------------------------

from contextlib import suppress


def parse_bool(value: str) -> bool:
    """bool"""
    if isinstance(value, str):
        with suppress(Exception):
            return float(value) >= 0
        return value.lower() in ("yes", "true", "y", "t")
    return bool(value)
