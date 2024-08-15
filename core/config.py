import sys
from pathlib import Path

FROZEN = getattr(sys, "frozen", False)
FIELD_FILENAME = "fields.py"

INTERNAL = Path("_internal")
OUTPUT_PATH = Path("output")
TEMPLATES_PATH = INTERNAL / "templates" if FROZEN else Path("templates")
