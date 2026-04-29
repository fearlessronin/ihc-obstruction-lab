"""Shadow-selector records."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ihc_lab.groups import FiniteAbelianGroup


@dataclass
class ShadowSelector:
    source_group: FiniteAbelianGroup
    selected_group: FiniteAbelianGroup
    selection_type: str
    coefficient: int | None = None
    active_sequence: str | None = None
    status: str = "unknown"
    comments: str | None = None

    def __post_init__(self) -> None:
        self.source_group = FiniteAbelianGroup.from_dict(self.source_group)
        self.selected_group = FiniteAbelianGroup.from_dict(self.selected_group)
        if self.coefficient is not None:
            self.coefficient = int(self.coefficient)

    def validate_z4_order_two_shadow(self) -> bool:
        return (
            self.source_group.cyclic_factors == [4]
            and self.selected_group.cyclic_factors == [2]
            and self.coefficient == 2
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_group": self.source_group.to_dict(),
            "selected_group": self.selected_group.to_dict(),
            "selection_type": self.selection_type,
            "coefficient": self.coefficient,
            "active_sequence": self.active_sequence,
            "status": self.status,
            "comments": self.comments,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any] | "ShadowSelector") -> "ShadowSelector":
        if isinstance(data, cls):
            return data
        return cls(
            source_group=FiniteAbelianGroup.from_dict(data["source_group"]),
            selected_group=FiniteAbelianGroup.from_dict(data["selected_group"]),
            selection_type=data["selection_type"],
            coefficient=data.get("coefficient"),
            active_sequence=data.get("active_sequence"),
            status=data.get("status", "unknown"),
            comments=data.get("comments"),
        )
