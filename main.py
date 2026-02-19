"""
Let's Do. | SignIT – Entry-Point.

Startet die SignIT GUI-Anwendung zum Signieren
von EXE-Dateien mit Code-Signing-Zertifikaten aus dem
Windows-Zertifikatsspeicher.

Projekt:  Let's Do. | SignIT
Lizenz:   Apache License 2.0
"""

from __future__ import annotations

import os
import sys

# ── Zentrale App-Konstanten ──────────────────────────────
APP_VERSION = "4.2"
APP_NAME = "Let's Do. | SignIT"
APP_AUTHOR = "Let's Do. - Inh. Peter Seidl"
# ─────────────────────────────────────────────────────────


def _setup_path() -> None:
    """
    Stellt sicher, dass das Projektverzeichnis im Python-Pfad liegt.
    Notwendig fuer PyInstaller-Kompatibilitaet.
    """
    if getattr(sys, "frozen", False):
        # PyInstaller-Bundle
        base = sys._MEIPASS  # type: ignore[attr-defined]
    else:
        base = os.path.dirname(os.path.abspath(__file__))

    if base not in sys.path:
        sys.path.insert(0, base)


def main() -> None:
    """Startet die Anwendung."""
    _setup_path()

    from gui.app import SignITApp

    app = SignITApp()
    app.mainloop()


if __name__ == "__main__":
    main()
