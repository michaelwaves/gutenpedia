from dataclasses import dataclass
from sqlalchemy import Table
from pathlib import Path


@dataclass
class DatasetSpec:
    name: str
    table: Table
    field_map: dict
    link_template: str
    base_dir: Path

    @property
    def insertable_cols(self) -> set[str]:
        return {
            c.name
            for c in self.table.columns
            if not c.primary_key and c.server_default is None
        }
