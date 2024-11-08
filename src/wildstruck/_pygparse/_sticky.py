# ----------------------------------------------------------------------------------------------
# Copyright (C) Botni.Vision, Inc - Montreal, QC, Canada - All Rights Reserved
# Unauthorized copying, use, or modification to this file via any medium is strictly prohibited.
# This file is private and confidential.
# Contact: dev@botni.vision
# ----------------------------------------------------------------------------------------------

from __future__ import annotations
from typing import Any, Callable, List, Tuple

from ._repeatable import Repeatable


class Sticky(Repeatable):
    """WARNING: Must be instantiated."""

    def __init__(
        self,
        constructor: Callable[[List[Tuple[str, ...] | str]], Any] = lambda x: x,
        tupleLength: int = 1,
    ) -> None:
        """
        A special Repeatable contructor that keeps accumulating until a new arg is passed.

        Args:
            constructor:
                The finalizer for the collection. Needs to accept a list of strings and be able to
                convert it into the final type as required by the the associated CLI's corresponding
                arg/kwarg. The default will return a list of strings.

            tupleLength:
                How many command line parameters must be consumed to create one list item tuple.
        """
        super().__init__(constructor, tupleLength)
