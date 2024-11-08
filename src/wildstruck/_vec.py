from __future__ import annotations
from dataclasses import dataclass
from functools import partial, singledispatchmethod
from itertools import chain, product
from math import ceil, floor, prod, sqrt
from operator import add, floordiv, invert, mod, mul, neg, sub, truediv
import random
from statistics import mean, median
import sys
from typing import Any, Callable, Generic, Iterable, Iterator, Optional, Sequence, Tuple, TypeVar


T = TypeVar("T")


@dataclass(frozen=True, init=False)
class Vec(Generic[T]):
    values: Tuple[T, ...]
    size: int

    def __init__(self, *values: T, size: Optional[int] = None) -> None:
        object.__setattr__(self, "values", values)
        if size is None:
            size = len(values)
        else:
            if len(values) != size:
                raise ValueError(f"{self.__class__.__name__} must contain exactly {size} values")
        object.__setattr__(self, "size", len(values))

    @property
    def x(self) -> T:
        return self[0]  # type: ignore # __getitem__ is @singledispatch

    @property
    def y(self) -> T:
        return self[1]  # type: ignore

    @property
    def z(self) -> T:
        return self[2]  # type: ignore

    @property
    def w(self) -> T:
        return self[3]  # type: ignore

    @property
    def min(self) -> T:
        return min(self.values)  # type: ignore

    @property
    def max(self) -> T:
        return max(self.values)  # type: ignore

    @property
    def median(self) -> T:
        return median(self.values)  # type: ignore

    @property
    def mean(self) -> T:
        return mean(self.values)  # type: ignore

    @property
    def sum(self) -> T:
        return sum(self.values)  # type: ignore

    @property
    def prod(self) -> T:
        return prod(self.values)  # type: ignore

    @property
    def reversed(self: V) -> V:
        return self.__class__(tuple(reversed(self.values)))

    @property
    def normalized(self) -> T:
        return self / self.magnitude  # type: ignore

    @property
    def magnitude(self) -> T:
        return sqrt(self.magnitudeSquared)  # type: ignore

    @property
    def magnitudeSquared(self) -> T:
        return self.map(lambda v: v**2).sum

    def root(self: V, other) -> V:
        return self ** (1 / other)

    def dot(self: V, other: V) -> V:
        return self.map(mul, other).sum

    def replace(self: V, index: int, value: T) -> V:
        return self.map(lambda v, i: (value if i == index else v), range(self.size))

    @staticmethod
    def _as_iterator(value: Any, size: int) -> Iterator:
        """Ensures that the given value is an Iterable for mapping purposes."""
        if isinstance(value, Iterable):
            yield from value
        else:
            for _ in range(size):
                yield value

    def map(self: V, function: Callable, *others) -> V:
        return self.__class__(
            *map(function, self, *(Vec._as_iterator(o, self.size) for o in others))
        )

    def chain(self: V, other: V) -> V:
        return self.__class__(*(chain(self, other)))

    def index(self, value: T, start: Optional[int] = None, stop: Optional[int] = None) -> int:
        return self.values.index(value, start or 0, stop or sys.maxsize)

    def export_string(
        self, template: str = "{!r}", sep: str = ", ", ends: Sequence[str] = "()"
    ) -> str:
        return ends[0] + sep.join(template.format(v) for v in self) + ends[1]

    def __getattribute__(self, __name) -> Any:
        if (
            1 < len(__name) <= 4
            and all(c in "xyzw" for c in __name)
            and list(set(__name)) == list(__name)
        ):
            return self.__class__(tuple(getattr(self, a) for a in __name))  # type: ignore
        return super().__getattribute__(__name)

    def __iter__(self) -> Iterator[T]:
        yield from self.values

    def __len__(self) -> int:
        return self.size

    @singledispatchmethod
    def __getitem__(self: V, key: Any) -> V | T:
        raise TypeError(f"Index type must be int or slice, not {type(key).__name__}")

    @__getitem__.register(int)
    def _get_at_index(self, index: int) -> T:
        return self.values[index]

    @__getitem__.register(slice)
    def _get_slice(self: V, key: slice) -> V:
        return self.__class__(self.values[key])

    def __eq__(self, other) -> bool:
        return all(a == b for a, b in zip(self, self._as_iterator(other, self.size)))

    def __ne__(self, other) -> bool:
        return any(a != b for a, b in zip(self, self._as_iterator(other, self.size)))

    def __add__(self: V, other) -> V:
        return self.map(add, other)

    __radd__ = __add__

    def __sub__(self: V, other) -> V:
        return self.map(sub, other)

    def __rsub__(self: V, other) -> V:
        return other - self

    def __mul__(self: V, other) -> V:
        return self.map(mul, other)

    __rmul__ = __mul__

    def __truediv__(self: V, other) -> V:
        return self.map(truediv, other)

    def __rtruediv__(self: V, other) -> V:
        return other / self

    def __floordiv__(self: V, other) -> V:
        return self.map(floordiv, other)

    def __rfloordiv__(self: V, other) -> V:
        return other // self

    def __mod__(self: V, other) -> V:
        return self.map(mod, other)

    def __rmod__(self: V, other) -> V:
        return other % self

    def __pow__(self: V, other) -> V:
        return self.map(pow, other)

    def __rpow__(self: V, other) -> V:
        return other**self

    def __neg__(self: V) -> V:
        return self.map(neg)

    def __abs__(self: V) -> V:
        return self.map(abs)

    def __invert__(self: V) -> V:
        return self.map(invert)

    def __round__(self: V, decimals: int = 0) -> V:
        return self.map(partial(round, ndigits=decimals))

    def __floor__(self: V) -> V:
        return self.map(floor)

    def __ceil__(self: V) -> V:
        return self.map(ceil)

    def __matmul__(self: V, other) -> V:
        return self.map(product, other)

    def __rmatmul__(self: V, other) -> V:
        return other @ self

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{repr(self.values)}"

    def __str__(self) -> str:
        return repr(self)


class Vec2(Vec[T]):
    def __init__(self, *values: T) -> None:
        super().__init__(*values, size=2)

    @staticmethod
    def Zero() -> "Vec2":
        return Vec2(0, 0)

    @staticmethod
    def One() -> "Vec2":
        return Vec2(1, 1)

    @staticmethod
    def Right() -> "Vec2":
        return Vec2(1, 0)

    @staticmethod
    def Up() -> "Vec2":
        return Vec2(0, 1)

    @staticmethod
    def Random() -> "Vec2":
        return Vec2(*(random.random() for _ in range(2)))


class Vec3(Vec[T]):
    def __init__(self, *values: T) -> None:
        super().__init__(*values, size=3)

    @staticmethod
    def Zero() -> "Vec3":
        return Vec3(0, 0, 0)

    @staticmethod
    def One() -> "Vec3":
        return Vec3(1, 1, 1)

    @staticmethod
    def Right() -> "Vec3":
        return Vec3(1, 0, 0)

    @staticmethod
    def Up() -> "Vec3":
        return Vec3(0, 1, 0)

    @staticmethod
    def Forward() -> "Vec3":
        return Vec3(0, 0, 1)

    @staticmethod
    def Random() -> "Vec3":
        return Vec3(*(random.random() for _ in range(3)))


class Vec4(Vec[T]):
    def __init__(self, *values: T) -> None:
        super().__init__(*values, size=4)

    @staticmethod
    def Zero() -> "Vec4":
        return Vec4(0, 0, 0, 0, 0)

    @staticmethod
    def One() -> "Vec4":
        return Vec4(1, 1, 1, 1, 1)

    @staticmethod
    def Right() -> "Vec4":
        return Vec4(1, 0, 0, 0)

    @staticmethod
    def Up() -> "Vec4":
        return Vec4(0, 1, 0, 0)

    @staticmethod
    def Forward() -> "Vec4":
        return Vec4(0, 0, 1, 0)

    @staticmethod
    def Ana() -> "Vec4":
        return Vec4(0, 0, 0, 1)

    @staticmethod
    def Random() -> "Vec4":
        return Vec4(*(random.random() for _ in range(4)))


V = TypeVar("V", bound=Vec)
