"""
Let's Do. | SignIT – Hilfsfunktionen.

Enthält Utility-Funktionen wie die Suche nach signtool.exe
und Pfad-Validierung.
"""

from __future__ import annotations

import os
import shutil
import glob
from pathlib import Path
from typing import List, Optional


# Bekannte Installationspfade für signtool.exe
SIGNTOOL_SEARCH_PATHS = [
    r"C:\Program Files (x86)\Windows Kits\10\bin",
    r"C:\Program Files (x86)\Windows Kits\8.1\bin",
    r"C:\Program Files (x86)\Windows Kits\8.0\bin",
    r"C:\Program Files\Windows Kits\10\bin",
    r"C:\Program Files (x86)\Microsoft SDKs\Windows\v10.0A\bin",
    r"C:\Program Files (x86)\Microsoft SDKs\ClickOnce\SignTool",
]

# Gängige Timestamp-Server
TIMESTAMP_SERVERS = [
    ("DigiCert (Standard)", "http://timestamp.digicert.com"),
    ("Sectigo", "http://timestamp.sectigo.com"),
    ("GlobalSign", "http://timestamp.globalsign.com/tsa/r6advanced1"),
    ("Comodo", "http://timestamp.comodoca.com/rfc3161"),
    ("SSL.com", "http://ts.ssl.com"),
    ("Entrust", "http://timestamp.entrust.net/TSS/RFC3161sha2TS"),
]


def find_signtool_in_path() -> Optional[str]:
    """
    Sucht signtool.exe im System-PATH.

    Returns:
        Pfad zu signtool.exe oder None
    """
    result = shutil.which("signtool.exe")
    if result:
        return str(Path(result).resolve())
    return None


def find_signtool_in_windows_kits() -> List[str]:
    """
    Durchsucht bekannte Windows SDK-Installationspfade nach signtool.exe.

    Returns:
        Liste gefundener signtool.exe-Pfade (neueste zuerst)
    """
    found: List[str] = []

    for base_path in SIGNTOOL_SEARCH_PATHS:
        if not os.path.exists(base_path):
            continue

        # Rekursiv nach signtool.exe suchen
        pattern = os.path.join(base_path, "**", "signtool.exe")
        matches = glob.glob(pattern, recursive=True)
        found.extend(matches)

    # Doppelte entfernen und nach Pfad sortieren (neuere SDKs = höhere Versionen)
    seen = set()
    unique: List[str] = []
    for p in sorted(found, reverse=True):
        norm = os.path.normpath(p).lower()
        if norm not in seen:
            seen.add(norm)
            unique.append(os.path.normpath(p))

    return unique


def find_signtool() -> Optional[str]:
    """
    Findet signtool.exe – erst im PATH, dann in Windows SDK-Ordnern.

    Returns:
        Pfad zu signtool.exe oder None
    """
    # Zuerst im PATH suchen
    path_result = find_signtool_in_path()
    if path_result:
        return path_result

    # Dann in bekannten Installationsordnern
    kit_results = find_signtool_in_windows_kits()
    if kit_results:
        # Bevorzuge x64-Version
        for p in kit_results:
            if "x64" in p.lower():
                return p
        return kit_results[0]

    return None


def validate_signtool(path: str) -> bool:
    """
    Prüft, ob der angegebene Pfad eine gültige signtool.exe ist.

    Args:
        path: Pfad zur signtool.exe

    Returns:
        True wenn die Datei existiert und 'signtool' im Namen hat
    """
    if not path:
        return False
    p = Path(path)
    return p.exists() and p.is_file() and "signtool" in p.name.lower()


def format_file_size(size_bytes: int) -> str:
    """Formatiert Dateigröße in menschenlesbare Form."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
