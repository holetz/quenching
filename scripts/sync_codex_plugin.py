#!/usr/bin/env python3
"""Compatibility launcher for the distributed components translator."""
from __future__ import annotations

import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "plugins/quenching/assets/bin"))
from quenching.components.commands.translate import main


if __name__ == "__main__":
    raise SystemExit(main())
