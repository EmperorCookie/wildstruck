# ----------------------------------------------------------------------------------------------
# Copyright (C) Botni.Vision, Inc - Montreal, QC, Canada - All Rights Reserved
# Unauthorized copying, use, or modification to this file via any medium is strictly prohibited.
# This file is private and confidential.
# Contact: dev@botni.vision
# ----------------------------------------------------------------------------------------------

from __future__ import annotations
from typing import Callable, Generic, List, Sequence, Tuple, TypeVar


T = TypeVar("T")


class Repeatable(Generic[T]):
    """WARNING: Must be instantiated."""

    def __init__(
        self,
        constructor: Callable[[List[Tuple[str, ...] | str]], T] = lambda x: x,
        tupleLength: int = 1,
    ) -> None:
        """
        A special constructor that allows an arg or kwarg to be supplied more than once with special
        behaviour.

        Args:
            constructor:
                The finalizer for the collection. Needs to accept a list of strings and be able to
                convert it into the final type as required by the the associated CLI's corresponding
                arg/kwarg. The default will return a list of strings.

            tupleLength:
                How many command line parameters must be consumed to create one list item tuple.
        """
        self.constructor = constructor
        self.tupleLength = tupleLength
        self.items: List[Tuple[str, ...] | str] = []

    def __call__(self, *values: str) -> Repeatable:
        """
        Adds a value to the list of items.

        Args:
            *values:
                The strings to add.
        """
        if len(values) == 0:
            raise ValueError("Must provide at least 1 value")
        self.items.append(values if len(values) > 1 else values[0])
        return self

    def construct(self, items: List[Tuple[str, ...] | str]) -> T:
        """
        Constructs the final value.

        Args:
            *items:
                The amassed list of parameter tuples.

        Returns:
            The fully typed value as returned by the constructor.
        """
        return self.constructor(items)
