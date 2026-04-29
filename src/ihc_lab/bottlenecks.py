"""Proof bottleneck records."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ihc_lab.enums import BottleneckLabel, parse_enum


@dataclass
class Bottleneck:
    label: BottleneckLabel
    description: str
    required_resolution: str | None = None
    comments: str | None = None

    def __post_init__(self) -> None:
        self.label = parse_enum(BottleneckLabel, self.label)

    def to_dict(self) -> dict[str, Any]:
        return {
            "label": self.label.value,
            "description": self.description,
            "required_resolution": self.required_resolution,
            "comments": self.comments,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any] | "Bottleneck") -> "Bottleneck":
        if isinstance(data, cls):
            return data
        return cls(
            label=parse_enum(BottleneckLabel, data["label"]),
            description=data["description"],
            required_resolution=data.get("required_resolution"),
            comments=data.get("comments"),
        )
