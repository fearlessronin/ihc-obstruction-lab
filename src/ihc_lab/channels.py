"""Main obstruction-channel row model."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ihc_lab.cup_products import CupProductCandidate
from ihc_lab.enums import (
    BottleneckLabel,
    ChannelLabel,
    ComputabilityLevel,
    ObstructionStatus,
    OperationLabel,
    SurvivalStatus,
    TrustLevel,
    parse_enum,
)
from ihc_lab.local_packages import LocalPackage
from ihc_lab.shadows import ShadowSelector
from ihc_lab.trajectories import TorsionTrajectory


@dataclass
class ObstructionChannel:
    id: str
    display_name: str
    source_corpus: str
    trust_level: TrustLevel
    geometry_or_package: str
    channel_labels: list[ChannelLabel] = field(default_factory=list)
    source_packages: list[str] = field(default_factory=list)
    active_operations: list[OperationLabel] = field(default_factory=list)
    survival_status: SurvivalStatus = SurvivalStatus.unknown
    obstruction_status: ObstructionStatus = ObstructionStatus.unknown
    computability_level: ComputabilityLevel = ComputabilityLevel.level_0_metadata
    bottleneck: BottleneckLabel = BottleneckLabel.unknown
    citation_keys: list[str] = field(default_factory=list)
    comments: str | None = None
    local_package: LocalPackage | None = None
    shadow_selector: ShadowSelector | None = None
    torsion_trajectory: TorsionTrajectory | None = None
    cup_product_candidate: CupProductCandidate | None = None

    def __post_init__(self) -> None:
        if not self.id or not self.id.strip():
            raise ValueError("id must be nonempty")
        if not self.display_name or not self.display_name.strip():
            raise ValueError("display_name must be nonempty")

        self.trust_level = parse_enum(TrustLevel, self.trust_level)
        self.channel_labels = [parse_enum(ChannelLabel, item) for item in self.channel_labels]
        self.active_operations = [
            parse_enum(OperationLabel, item) for item in self.active_operations
        ]
        self.survival_status = parse_enum(SurvivalStatus, self.survival_status)
        self.obstruction_status = parse_enum(ObstructionStatus, self.obstruction_status)
        self.computability_level = parse_enum(ComputabilityLevel, self.computability_level)
        self.bottleneck = parse_enum(BottleneckLabel, self.bottleneck)

        if self.local_package is not None:
            self.local_package = LocalPackage.from_dict(self.local_package)
        if self.shadow_selector is not None:
            self.shadow_selector = ShadowSelector.from_dict(self.shadow_selector)
        if self.torsion_trajectory is not None:
            self.torsion_trajectory = TorsionTrajectory.from_dict(self.torsion_trajectory)
        if self.cup_product_candidate is not None:
            self.cup_product_candidate = CupProductCandidate.from_dict(
                self.cup_product_candidate
            )

        labels = set(self.channel_labels)
        if (
            ChannelLabel.nodal_free_relation in labels
            and ChannelLabel.local_discriminant in labels
        ):
            raise ValueError("nodal_free_relation rows cannot also be local_discriminant")

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "display_name": self.display_name,
            "source_corpus": self.source_corpus,
            "trust_level": self.trust_level.value,
            "geometry_or_package": self.geometry_or_package,
            "channel_labels": [item.value for item in self.channel_labels],
            "source_packages": list(self.source_packages),
            "active_operations": [item.value for item in self.active_operations],
            "survival_status": self.survival_status.value,
            "obstruction_status": self.obstruction_status.value,
            "computability_level": self.computability_level.value,
            "bottleneck": self.bottleneck.value,
            "citation_keys": list(self.citation_keys),
            "comments": self.comments,
            "local_package": self.local_package.to_dict() if self.local_package else None,
            "shadow_selector": self.shadow_selector.to_dict() if self.shadow_selector else None,
            "torsion_trajectory": (
                self.torsion_trajectory.to_dict() if self.torsion_trajectory else None
            ),
            "cup_product_candidate": (
                self.cup_product_candidate.to_dict() if self.cup_product_candidate else None
            ),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any] | "ObstructionChannel") -> "ObstructionChannel":
        if isinstance(data, cls):
            return data
        return cls(
            id=data["id"],
            display_name=data["display_name"],
            source_corpus=data["source_corpus"],
            trust_level=parse_enum(TrustLevel, data["trust_level"]),
            geometry_or_package=data["geometry_or_package"],
            channel_labels=[parse_enum(ChannelLabel, item) for item in data["channel_labels"]],
            source_packages=list(data.get("source_packages", [])),
            active_operations=[
                parse_enum(OperationLabel, item) for item in data.get("active_operations", [])
            ],
            survival_status=parse_enum(SurvivalStatus, data.get("survival_status", "unknown")),
            obstruction_status=parse_enum(
                ObstructionStatus, data.get("obstruction_status", "unknown")
            ),
            computability_level=parse_enum(
                ComputabilityLevel, data.get("computability_level", "level_0_metadata")
            ),
            bottleneck=parse_enum(BottleneckLabel, data.get("bottleneck", "unknown")),
            citation_keys=list(data.get("citation_keys", [])),
            comments=data.get("comments"),
            local_package=(
                LocalPackage.from_dict(data["local_package"])
                if data.get("local_package") is not None
                else None
            ),
            shadow_selector=(
                ShadowSelector.from_dict(data["shadow_selector"])
                if data.get("shadow_selector") is not None
                else None
            ),
            torsion_trajectory=(
                TorsionTrajectory.from_dict(data["torsion_trajectory"])
                if data.get("torsion_trajectory") is not None
                else None
            ),
            cup_product_candidate=(
                CupProductCandidate.from_dict(data["cup_product_candidate"])
                if data.get("cup_product_candidate") is not None
                else None
            ),
        )

    def markdown_summary(self) -> str:
        labels = ", ".join(label.value for label in self.channel_labels)
        local = ""
        if self.local_package is not None:
            local = f" Local group: `{self.local_package.group_summary()}`."
        return (
            f"### {self.display_name}\n\n"
            f"- id: `{self.id}`\n"
            f"- channels: {labels}\n"
            f"- trust: `{self.trust_level.value}`\n"
            f"- obstruction status: `{self.obstruction_status.value}`\n"
            f"- bottleneck: `{self.bottleneck.value}`\n"
            f"{local}"
        )
