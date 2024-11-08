# ----------------------------------------------------------------------------------------------
# Copyright (C) Botni.Vision, Inc - Montreal, QC, Canada - All Rights Reserved
# Unauthorized copying, use, or modification to this file via any medium is strictly prohibited.
# This file is private and confidential.
# Contact: dev@botni.vision
# ----------------------------------------------------------------------------------------------

from typing import Callable, Dict, List, Tuple, TypeVar


KT = TypeVar("KT")
VT = TypeVar("VT")


def build_dict_parser(
    keyParser: Callable[[str], KT],
    valParser: Callable[[str], VT],
    docstringType: bool = False,
) -> Tuple[Callable[[List[Tuple[str, str]]], Dict[KT, VT]], int]:
    """
    Creates a typed dict parser.

    Args:
        keyParser:
            A parser for the key.

        valParser:
            A parser for the value.

        docstringType:
            If `True`, the method will have a docstring for the key and value types.

    Returns:
        A (parser_method, valueCount) tuple.
    """

    def parse_dict(values: List[Tuple[str, str]]) -> Dict[KT, VT]:
        return {keyParser(k): valParser(v) for k, v in values}

    if docstringType:
        keyDoc = keyParser.__name__ if isinstance(keyParser, type) else (keyParser.__doc__ or "key")
        valDoc = (
            valParser.__name__ if isinstance(valParser, type) else (valParser.__doc__ or "value")
        )
        parse_dict.__doc__ = f"{keyDoc} {valDoc}"
    return parse_dict, 2
