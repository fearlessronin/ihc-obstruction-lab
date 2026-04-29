"""Generator mechanism records."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ihc_lab.enums import BottleneckLabel, ChannelLabel, parse_enum


@dataclass
class GeneratorMechanism:
    name: str
    channel_label: ChannelLabel
    description: str
    required_inputs: list[str] = field(default_factory=list)
    output_type: str = ""
    typical_bottleneck: BottleneckLabel = BottleneckLabel.unknown
    comments: str | None = None

    def __post_init__(self) -> None:
        self.channel_label = parse_enum(ChannelLabel, self.channel_label)
        self.typical_bottleneck = parse_enum(BottleneckLabel, self.typical_bottleneck)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "channel_label": self.channel_label.value,
            "description": self.description,
            "required_inputs": list(self.required_inputs),
            "output_type": self.output_type,
            "typical_bottleneck": self.typical_bottleneck.value,
            "comments": self.comments,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any] | "GeneratorMechanism") -> "GeneratorMechanism":
        if isinstance(data, cls):
            return data
        return cls(
            name=data["name"],
            channel_label=parse_enum(ChannelLabel, data["channel_label"]),
            description=data["description"],
            required_inputs=list(data.get("required_inputs", [])),
            output_type=data.get("output_type", ""),
            typical_bottleneck=parse_enum(
                BottleneckLabel, data.get("typical_bottleneck", "unknown")
            ),
            comments=data.get("comments"),
        )
