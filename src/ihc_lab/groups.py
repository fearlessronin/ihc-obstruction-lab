"""Finite abelian group helpers."""

from __future__ import annotations

from dataclasses import dataclass, field
from functools import reduce
from operator import mul
from typing import Any


@dataclass(frozen=True)
class FiniteAbelianGroup:
    """Finite abelian group in normalized invariant-factor style."""

    cyclic_factors: list[int] = field(default_factory=list)

    def __post_init__(self) -> None:
        factors = [int(factor) for factor in self.cyclic_factors]
        if any(factor <= 0 for factor in factors):
            raise ValueError("cyclic factors must be positive integers")
        normalized = sorted(factor for factor in factors if factor != 1)
        object.__setattr__(self, "cyclic_factors", normalized)

    @classmethod
    def trivial(cls) -> "FiniteAbelianGroup":
        return cls([])

    def is_trivial(self) -> bool:
        return not self.cyclic_factors

    def order(self) -> int:
        if self.is_trivial():
            return 1
        return reduce(mul, self.cyclic_factors, 1)

    def contains_subgroup_order(self, n: int) -> bool:
        if n <= 0:
            raise ValueError("subgroup order must be positive")
        return self.order() % n == 0

    def has_element_order_dividing(self, n: int) -> bool:
        if n <= 0:
            raise ValueError("element order divisor must be positive")
        return all(factor % n == 0 or n % factor == 0 for factor in self.cyclic_factors)

    def to_dict(self) -> dict[str, list[int]]:
        return {"cyclic_factors": list(self.cyclic_factors)}

    @classmethod
    def from_dict(cls, data: dict[str, Any] | "FiniteAbelianGroup") -> "FiniteAbelianGroup":
        if isinstance(data, cls):
            return data
        return cls(cyclic_factors=list(data.get("cyclic_factors", [])))

    def __str__(self) -> str:
        if self.is_trivial():
            return "0"
        return " ⊕ ".join(f"Z/{factor}Z" for factor in self.cyclic_factors)
