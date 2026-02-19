"""
Let's Do. | SignIT – Ueber-Dialog.

Zeigt Informationen ueber die Anwendung, den Herausgeber,
Build-Details und Lizenzhinweise.
"""

from __future__ import annotations

import os
import platform
import sys
import webbrowser
from datetime import datetime
from typing import Optional

import customtkinter as ctk

try:
    from PIL import Image

    HAS_PIL = True
except ImportError:
    HAS_PIL = False


def _resource_path(relative: str) -> str:
    """Gibt den Pfad zu einer Ressource zurueck (PyInstaller-kompatibel)."""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative)  # type: ignore[attr-defined]
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), relative)


def _get_build_date() -> str:
    """
    Ermittelt das Build-Datum.

    Bei einer PyInstaller-EXE wird das Aenderungsdatum der EXE verwendet,
    ansonsten das aktuelle Datum.
    """
    if getattr(sys, "frozen", False):
        try:
            exe_path = sys.executable
            mtime = os.path.getmtime(exe_path)
            return datetime.fromtimestamp(mtime).strftime("%d.%m.%Y")
        except Exception:
            pass
    return datetime.now().strftime("%d.%m.%Y")


def _get_platform_info() -> str:
    """Gibt eine lesbare Plattform-Beschreibung zurueck."""
    ver = platform.version()
    arch = platform.machine()
    release = platform.release()
    return f"Windows {release} ({arch})"


def _get_python_version() -> str:
    """Gibt die Python-Version zurueck."""
    return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"


class AboutDialog(ctk.CTkToplevel):
    """
    Modaler 'Ueber SignIT'-Dialog.

    Zeigt App-Info, Herausgeber-Daten, Build-Details und Lizenz.
    """

    WEBSITE_URL = "https://lets-do.media"
    EMAIL = "pseidl@lets-do.media"

    def __init__(self, master, app_version: str = "1.0.0", **kwargs):
        super().__init__(master, **kwargs)

        self._app_version = app_version
        self._icon_image = None

        # --- Fenster-Konfiguration ---
        self.title("Ueber SignIT")
        self.geometry("480x540")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        # Icon setzen
        icon_path = _resource_path("assets/icon.ico")
        if os.path.exists(icon_path):
            self.after(200, lambda: self.iconbitmap(icon_path))

        # Zentrieren relativ zum Hauptfenster
        self.after(10, lambda: self._center_on_parent(master))

        # --- Inhalt aufbauen ---
        self._build_content()

        # Focus
        self.focus_force()

    def _center_on_parent(self, parent) -> None:
        """Zentriert den Dialog ueber dem Hauptfenster."""
        self.update_idletasks()
        pw = parent.winfo_width()
        ph = parent.winfo_height()
        px = parent.winfo_x()
        py = parent.winfo_y()
        w = self.winfo_width()
        h = self.winfo_height()
        x = px + (pw - w) // 2
        y = py + (ph - h) // 2
        self.geometry(f"+{x}+{y}")

    def _build_content(self) -> None:
        """Erstellt den gesamten Dialog-Inhalt."""

        # Hauptcontainer
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=24, pady=20)

        # ==============================================
        # Header: Icon + Titel
        # ==============================================
        header = ctk.CTkFrame(container, fg_color="transparent")
        header.pack(fill="x", pady=(0, 16))

        # Icon laden (falls Pillow vorhanden)
        icon_path = _resource_path("assets/icon.ico")
        if HAS_PIL and os.path.exists(icon_path):
            try:
                img = Image.open(icon_path)
                img = img.resize((64, 64), Image.LANCZOS)
                # FIX #5: Bildreferenz am Objekt halten, damit sie nicht GC'ed wird.
                self._icon_image = ctk.CTkImage(
                    light_image=img,
                    dark_image=img,
                    size=(64, 64),
                )
                icon_label = ctk.CTkLabel(header, image=self._icon_image, text="")
                icon_label.pack(pady=(0, 8))
            except Exception:
                pass

        # Titel
        ctk.CTkLabel(
            header,
            text="Let's Do. | SignIT",
            font=ctk.CTkFont(size=24, weight="bold"),
        ).pack()

        # Untertitel
        ctk.CTkLabel(
            header,
            text="Code-Signing, einfach gemacht.",
            font=ctk.CTkFont(size=13),
            text_color="#888888",
        ).pack(pady=(2, 0))

        # ==============================================
        # Trennlinie
        # ==============================================
        ctk.CTkFrame(container, height=1, fg_color="#333333").pack(
            fill="x", pady=(0, 14)
        )

        # ==============================================
        # Info-Block: Version, Build, Plattform, Lizenz
        # ==============================================
        info_frame = ctk.CTkFrame(container, fg_color="#16213e", corner_radius=8)
        info_frame.pack(fill="x", pady=(0, 14))

        info_data = [
            ("Version", f"v{self._app_version}"),
            ("Build", _get_build_date()),
            ("Python", _get_python_version()),
            ("Plattform", _get_platform_info()),
            ("Lizenz", "Apache License 2.0"),
        ]

        for i, (label, value) in enumerate(info_data):
            row = ctk.CTkFrame(info_frame, fg_color="transparent")
            row.pack(
                fill="x",
                padx=16,
                pady=(8 if i == 0 else 2, 8 if i == len(info_data) - 1 else 2),
            )

            ctk.CTkLabel(
                row,
                text=label,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="#8899aa",
                width=90,
                anchor="w",
            ).pack(side="left")

            ctk.CTkLabel(
                row,
                text=value,
                font=ctk.CTkFont(size=12),
                text_color="#cccccc",
                anchor="w",
            ).pack(side="left")

        # ==============================================
        # Trennlinie
        # ==============================================
        ctk.CTkFrame(container, height=1, fg_color="#333333").pack(
            fill="x", pady=(0, 14)
        )

        # ==============================================
        # Herausgeber-Block
        # ==============================================
        pub_frame = ctk.CTkFrame(container, fg_color="transparent")
        pub_frame.pack(fill="x", pady=(0, 14))

        ctk.CTkLabel(
            pub_frame,
            text="Herausgeber",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#666666",
        ).pack(anchor="w")

        ctk.CTkLabel(
            pub_frame,
            text="Let's Do. - Inh. Peter Seidl",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w",
        ).pack(anchor="w", pady=(4, 0))

        ctk.CTkLabel(
            pub_frame,
            text="Bahnhofstrasse 67  |  85088 Vohburg",
            font=ctk.CTkFont(size=12),
            text_color="#aaaaaa",
            anchor="w",
        ).pack(anchor="w", pady=(2, 0))

        # E-Mail (klickbar)
        email_btn = ctk.CTkButton(
            pub_frame,
            text=self.EMAIL,
            font=ctk.CTkFont(size=12),
            text_color="#60a5fa",
            fg_color="transparent",
            hover_color="#1a2a4a",
            anchor="w",
            width=0,
            height=24,
            cursor="hand2",
            command=lambda: webbrowser.open(f"mailto:{self.EMAIL}"),
        )
        email_btn.pack(anchor="w", pady=(4, 0))

        # Website (klickbar)
        web_btn = ctk.CTkButton(
            pub_frame,
            text=self.WEBSITE_URL,
            font=ctk.CTkFont(size=12),
            text_color="#60a5fa",
            fg_color="transparent",
            hover_color="#1a2a4a",
            anchor="w",
            width=0,
            height=24,
            cursor="hand2",
            command=lambda: webbrowser.open(self.WEBSITE_URL),
        )
        web_btn.pack(anchor="w", pady=(0, 0))

        # ==============================================
        # Trennlinie
        # ==============================================
        ctk.CTkFrame(container, height=1, fg_color="#333333").pack(
            fill="x", pady=(0, 14)
        )

        # ==============================================
        # Footer: Copyright + Schliessen-Button
        # ==============================================
        footer = ctk.CTkFrame(container, fg_color="transparent")
        footer.pack(fill="x")

        year = datetime.now().year
        ctk.CTkLabel(
            footer,
            text=f"\u00a9 {year} Let's Do. - Alle Rechte vorbehalten.",
            font=ctk.CTkFont(size=11),
            text_color="#555555",
        ).pack(side="left")

        ctk.CTkButton(
            footer,
            text="Schliessen",
            width=100,
            height=32,
            font=ctk.CTkFont(size=13),
            command=self.destroy,
        ).pack(side="right")
