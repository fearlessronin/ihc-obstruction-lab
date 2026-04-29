"""Finite-coefficient input records."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class FiniteCoefficientInput:
    class_name: str
    variety_factor: str
    cohomological_degree: int
    twist: int
    coefficient: int
    source_type: str
    theorem_status: str
    comments: str | None = None

    def __post_init__(self) -> None:
        self.cohomological_degree = int(self.cohomological_degree)
        self.twist = int(self.twist)
        self.coefficient = int(self.coefficient)
        if self.cohomological_degree < 0:
            raise ValueError("cohomological_degree must be nonnegative")
        if self.twist < 0:
            raise ValueError("twist must be nonnegative")
        if self.coefficient < 2:
            raise ValueError("coefficient must be at least 2")

    def to_dict(self) -> dict[str, Any]:
        return {
            "class_name": self.class_name,
            "variety_factor": self.variety_factor,
            "cohomological_degree": self.cohomological_degree,
            "twist": self.twist,
            "coefficient": self.coefficient,
            "source_type": self.source_type,
            "theorem_status": self.theorem_status,
            "comments": self.comments,
        }

    @classmethod
    def from_dict(
        cls, data: dict[str, Any] | "FiniteCoefficientInput"
    ) -> "FiniteCoefficientInput":
        if isinstance(data, cls):
            return data
        return cls(
            class_name=data["class_name"],
            variety_factor=data["variety_factor"],
            cohomological_degree=int(data["cohomological_degree"]),
            twist=int(data["twist"]),
            coefficient=int(data["coefficient"]),
            source_type=data["source_type"],
            theorem_status=data["theorem_status"],
            comments=data.get("comments"),
        )
