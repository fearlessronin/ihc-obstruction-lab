"""Finite-coefficient cup-product and Bockstein candidates."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ihc_lab.enums import BottleneckLabel, ObstructionStatus, SurvivalStatus, parse_enum
from ihc_lab.finite_coefficients import FiniteCoefficientInput


@dataclass
class CupProductCandidate:
    inputs: list[FiniteCoefficientInput] = field(default_factory=list)
    target_codimension: int = 0
    coefficient: int = 2
    survival_status: SurvivalStatus = SurvivalStatus.unknown
    obstruction_status: ObstructionStatus = ObstructionStatus.unknown
    bottleneck: BottleneckLabel = BottleneckLabel.unknown
    comments: str | None = None

    def __post_init__(self) -> None:
        self.inputs = [FiniteCoefficientInput.from_dict(item) for item in self.inputs]
        self.target_codimension = int(self.target_codimension)
        self.coefficient = int(self.coefficient)
        self.survival_status = parse_enum(SurvivalStatus, self.survival_status)
        self.obstruction_status = parse_enum(ObstructionStatus, self.obstruction_status)
        self.bottleneck = parse_enum(BottleneckLabel, self.bottleneck)
        if self.target_codimension < 0:
            raise ValueError("target_codimension must be nonnegative")
        if self.coefficient < 2:
            raise ValueError("coefficient must be at least 2")

    def total_degree(self) -> int:
        return sum(item.cohomological_degree for item in self.inputs)

    def total_twist(self) -> int:
        return sum(item.twist for item in self.inputs)

    def expected_bockstein_degree(self) -> int:
        return 2 * self.target_codimension

    def expected_pre_bockstein_degree(self) -> int:
        return 2 * self.target_codimension - 1

    def is_degree_twist_valid(self) -> bool:
        return (
            self.total_degree() == self.expected_pre_bockstein_degree()
            and self.total_twist() == self.target_codimension
        )

    def bockstein_target_string(self) -> str:
        return f"H^{self.expected_bockstein_degree()}(-, Z({self.target_codimension}))"

    def finite_coefficient_source_string(self) -> str:
        return (
            f"H^{self.total_degree()}(-, "
            f"Z/{self.coefficient}({self.target_codimension}))"
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "inputs": [item.to_dict() for item in self.inputs],
            "target_codimension": self.target_codimension,
            "coefficient": self.coefficient,
            "survival_status": self.survival_status.value,
            "obstruction_status": self.obstruction_status.value,
            "bottleneck": self.bottleneck.value,
            "comments": self.comments,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any] | "CupProductCandidate") -> "CupProductCandidate":
        if isinstance(data, cls):
            return data
        return cls(
            inputs=[FiniteCoefficientInput.from_dict(item) for item in data.get("inputs", [])],
            target_codimension=int(data["target_codimension"]),
            coefficient=int(data["coefficient"]),
            survival_status=parse_enum(SurvivalStatus, data.get("survival_status", "unknown")),
            obstruction_status=parse_enum(
                ObstructionStatus, data.get("obstruction_status", "unknown")
            ),
            bottleneck=parse_enum(BottleneckLabel, data.get("bottleneck", "unknown")),
            comments=data.get("comments"),
        )
