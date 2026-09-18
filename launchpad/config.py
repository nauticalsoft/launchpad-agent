"""Load the Product Kit and the sites worklist."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field

KIT_PATH = Path(__file__).parent / "product_kit.yaml"
SITES_PATH = Path(__file__).parent / "sites.csv"


class ProductKit(BaseModel):
    name: str
    brand: str = ""
    url: str
    homepage: str = ""
    username: str
    username_fallbacks: list[str] = Field(default_factory=list)
    email: str = ""
    founder_name: str = ""
    tagline_60: str = ""
    short_desc_160: str = ""
    long_desc_500: str = ""
    long_desc_1000: str = ""
    categories: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)

    def usernames(self) -> list[str]:
        return [self.username, *self.username_fallbacks]


class Site(BaseModel):
    id: int
    platform: str
    url: str
    category: str = ""
    what_its_for: str = ""
    cost: str = ""
    pro_tips: str = ""


def load_kit(path: str | Path = KIT_PATH) -> ProductKit:
    raw: dict[str, Any] = yaml.safe_load(Path(path).read_text())
    return ProductKit(**raw)


def load_sites(path: str | Path = SITES_PATH) -> list[Site]:
    sites: list[Site] = []
    with Path(path).open() as fh:
        for row in csv.DictReader(fh):
            sites.append(
                Site(
                    id=int(row["#"]),
                    platform=row["Platform"],
                    url=row["Website"],
                    category=row.get("Category", ""),
                    what_its_for=row.get("What_Its_For", ""),
                    cost=row.get("Cost", ""),
                    pro_tips=row.get("Pro_Tips", ""),
                )
            )
    return sites
