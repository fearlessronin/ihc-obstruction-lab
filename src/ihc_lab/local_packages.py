"""Local singularity and discriminant packages."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ihc_lab.enums import ComputabilityLevel, parse_enum
from ihc_lab.groups import FiniteAbelianGroup


@dataclass
class LocalPackage:
    singularity_type: str
    dimension: int
    local_group: FiniteAbelianGroup
    discriminant_form: str | None = None
    link_model: str | None = None
    exceptional_lattice_matrix: list[list[int]] | None = None
    monodromy_matrix: list[list[int]] | None = None
    prime_support: list[int] = field(default_factory=list)
    computability_level: ComputabilityLevel = ComputabilityLevel.level_0_metadata
    comments: str | None = None

    def __post_init__(self) -> None:
        self.local_group = FiniteAbelianGroup.from_dict(self.local_group)
        self.computability_level = parse_enum(ComputabilityLevel, self.computability_level)
        self.prime_support = [int(prime) for prime in self.prime_support]

    def group_summary(self) -> str:
        return str(self.local_group)

    def to_dict(self) -> dict[str, Any]:
        return {
            "singularity_type": self.singularity_type,
            "dimension": self.dimension,
            "local_group": self.local_group.to_dict(),
            "discriminant_form": self.discriminant_form,
            "link_model": self.link_model,
            "exceptional_lattice_matrix": self.exceptional_lattice_matrix,
            "monodromy_matrix": self.monodromy_matrix,
            "prime_support": list(self.prime_support),
            "computability_level": self.computability_level.value,
            "comments": self.comments,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any] | "LocalPackage") -> "LocalPackage":
        if isinstance(data, cls):
            return data
        return cls(
            singularity_type=data["singularity_type"],
            dimension=int(data["dimension"]),
            local_group=FiniteAbelianGroup.from_dict(data["local_group"]),
            discriminant_form=data.get("discriminant_form"),
            link_model=data.get("link_model"),
            exceptional_lattice_matrix=data.get("exceptional_lattice_matrix"),
            monodromy_matrix=data.get("monodromy_matrix"),
            prime_support=list(data.get("prime_support", [])),
            computability_level=parse_enum(
                ComputabilityLevel, data.get("computability_level", "level_0_metadata")
            ),
            comments=data.get("comments"),
        )
