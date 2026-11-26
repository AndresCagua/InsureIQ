"""Command-line checks for the reproducible project foundation."""

from __future__ import annotations

import os
import sys


def doctor() -> None:
    """Check the runtime assumptions available inside the project container."""
    expected = (3, 12)
    actual = sys.version_info[:2]
    if actual != expected:
        raise SystemExit(
            f"Versión de Python incorrecta: se requiere {expected[0]}.{expected[1]}, "
            f"se encontró {actual[0]}.{actual[1]}"
        )
    print(f"Python correcto: {actual[0]}.{actual[1]}")
    print(f"Zona horaria configurada: {os.getenv('TZ', 'no configurada')}")
    print("Base reproducible InsureIQ: OK")


if __name__ == "__main__":
    doctor()
