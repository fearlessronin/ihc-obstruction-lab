"""Torsion trajectory records."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class TorsionTrajectory:
    birth: str
    form: str
    local_realization: str
    support_transport: str
    global_image: str
    brauer_comparison: str
    unramified_survival: str
    bockstein_image: str
    rational_death: str
    station_statuses: dict[str, str] = field(default_factory=dict)
    comments: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "birth": self.birth,
            "form": self.form,
            "local_realization": self.local_realization,
            "support_transport": self.support_transport,
            "global_image": self.global_image,
            "brauer_comparison": self.brauer_comparison,
            "unramified_survival": self.unramified_survival,
            "bockstein_image": self.bockstein_image,
            "rational_death": self.rational_death,
            "station_statuses": dict(self.station_statuses),
            "comments": self.comments,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any] | "TorsionTrajectory") -> "TorsionTrajectory":
        if isinstance(data, cls):
            return data
        return cls(
            birth=data["birth"],
            form=data["form"],
            local_realization=data["local_realization"],
            support_transport=data["support_transport"],
            global_image=data["global_image"],
            brauer_comparison=data["brauer_comparison"],
            unramified_survival=data["unramified_survival"],
            bockstein_image=data["bockstein_image"],
            rational_death=data["rational_death"],
            station_statuses=dict(data.get("station_statuses", {})),
            comments=data.get("comments"),
        )
