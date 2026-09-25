"""Frozen protocol loader and structural invariants.

Only scientific-preregistration files are read. No outcome or cache path is
accepted by this module.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Iterable, Sequence


ROOT = Path(__file__).resolve().parents[1]
DESIGN_DIR = ROOT / "02_DESIGN"
STUDY_ID = "UBOA_ROUTE_B_SYNTH_CONFIRMATORY_V1"
MASTER_SEED = "7fae9301e8e38493e1917601eef359468a74b79fab00cd4a31777da6074dc110"
RHO = Fraction(1, 2)
HORIZONS = (1, 3, 6)
LADDER = (Fraction(0), Fraction(1, 50), Fraction(1, 20))
LOCAL_ALPHA = Fraction(1, 20)
BURN_IN = 256
VALIDATION_ORIGINS = tuple(range(256, 320))
H_END = 325
EVALUATION_START = 325
OUTER_HISTORIES = 8
INNER_FUTURES = 4096
EXPECTED_CELLS = 10


@dataclass(frozen=True)
class Cell:
    cell_id: str
    branch: str
    loss: str
    eval_origins: int
    comparator_delta: Fraction | None
    comparator_gamma: float | None
    exact_theta: Fraction | None
    frozen_first_true_null: str | None

    @property
    def origin_offsets(self) -> tuple[int, ...]:
        return tuple(range(self.eval_origins))

    @property
    def absolute_origins(self) -> tuple[int, ...]:
        return tuple(range(EVALUATION_START, EVALUATION_START + self.eval_origins))

    @property
    def term_weight(self) -> Fraction:
        return Fraction(1, self.eval_origins * len(HORIZONS))


def _fraction_or_none(value: str) -> Fraction | None:
    value = value.strip()
    return Fraction(value) if value else None


def load_cells() -> tuple[Cell, ...]:
    with (DESIGN_DIR / "CELL_TABLE_ALL.tsv").open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    if len(rows) != EXPECTED_CELLS:
        raise ValueError(f"expected {EXPECTED_CELLS} frozen cells, got {len(rows)}")
    cells = []
    for row in rows:
        if row["horizons"] != "1;3;6" or row["ladder"] != "0;1/50;1/20":
            raise ValueError(f"frozen scope mismatch in {row['cell_id']}")
        if row["outer_histories"] != "8" or row["inner_futures_per_history"] != "4096":
            raise ValueError(f"frozen replication mismatch in {row['cell_id']}")
        if row["local_alpha"] != "1/20" or row["weights"] != "equal over all evaluation origin-horizon terms":
            raise ValueError(f"frozen testing mismatch in {row['cell_id']}")
        cells.append(
            Cell(
                cell_id=row["cell_id"],
                branch=row["branch"],
                loss=row["loss"],
                eval_origins=int(row["eval_origins"]),
                comparator_delta=_fraction_or_none(row["comparator_delta_exact"]),
                comparator_gamma=float(row["comparator_gamma"]) if row["comparator_gamma"] else None,
                exact_theta=_fraction_or_none(row["exact_theta"]),
                frozen_first_true_null=row["first_true_null"] or None,
            )
        )
    if len({cell.cell_id for cell in cells}) != EXPECTED_CELLS:
        raise ValueError("cell identifiers are not unique")
    return tuple(cells)


def expected_scope(eval_origins: int) -> tuple[tuple[int, int, Fraction], ...]:
    if eval_origins not in (256, 512):
        raise ValueError("evaluation-origin count is outside the frozen design")
    weight = Fraction(1, eval_origins * len(HORIZONS))
    return tuple((k, h, weight) for k in range(eval_origins) for h in HORIZONS)


def assert_frozen_scope(
    scope: Sequence[tuple[int, int, Fraction]], eval_origins: int
) -> None:
    expected = expected_scope(eval_origins)
    normalized = tuple((int(k), int(h), Fraction(w)) for k, h, w in scope)
    if normalized != expected:
        raise ValueError("scope mismatch: origins, horizons, order, or weights changed")


def first_true_null(truths: Iterable[bool]) -> int | None:
    values = tuple(bool(value) for value in truths)
    if len(values) != len(LADDER):
        raise ValueError("truth vector must match frozen ladder")
    return next((index for index, value in enumerate(values) if value), None)
