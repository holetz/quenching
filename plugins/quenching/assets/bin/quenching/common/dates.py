"""Today, as the ISO date every stamp is written in.

Moved verbatim out of `specs.py`."""
from __future__ import annotations

import datetime


def today() -> str:
    return datetime.date.today().isoformat()
