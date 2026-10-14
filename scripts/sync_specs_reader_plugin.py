#!/usr/bin/env python3
"""Compatibility entry point for the manifest-driven generated plugin distribution."""
from generate_plugin_modules import main

if __name__ == "__main__":
    raise SystemExit(main())
