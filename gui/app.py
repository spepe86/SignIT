"""
Let's Do. | SignIT – Hauptfenster & Layout.

Setzt das gesamte GUI zusammen: CertPanel, FilePanel, SignPanel, LogPanel.
Verwendet CustomTkinter für ein modernes, dunkles UI-Design.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Optional

import customtkinter as ctk

from core.certstore import CertInfo
from gui.about_dialog import AboutDialog
from gui.cert_panel import CertPanel
from gui.file_panel import FilePanel
from gui.log_panel import LogPanel
from gui.sign_panel import SignPanel


def _resource_path(relative: str) -> str:
    """Gibt den Pfad zu einer Ressource zurück (PyInstaller-kompatibel)."""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative)
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), relative)


class SignITApp(ctk.CTk):
    """
    Hauptfenster der Let's Do. | SignIT Anwendung.

    Organisiert den Workflow in einem scrollbaren, vertikalen Layout:
    1. Zertifikat auswählen
    2. Dateien auswählen
    3. SignTool-Pfad & Timestamp konfigurieren
    4. Signieren mit Live-Log
    """

    APP_TITLE = "Let's Do. | SignIT"
    MIN_WIDTH = 920
    MIN_HEIGHT = 700

    def __init__(self):
        super().__init__()

        # --- Fenster-Konfiguration ---
        self.title(self.APP_TITLE)
        self.geometry(f"{self.MIN_WIDTH}x{self.MIN_HEIGHT}")
        self.minsize(self.MIN_WIDTH, self.MIN_HEIGHT)

        # Icon setzen (falls vorhanden)
        icon_path = _resource_path("assets/icon.ico")
        if os.path.exists(icon_path):
            self.iconbitmap(icon_path)

        # Dark-Mode als Standard
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # --- Layout ---
        self._build_ui()

        # --- Statusleiste ---
        self._build_statusbar()

        # Initiale Log-Nachricht
        self._log_panel.log_header("Let's Do. | SignIT gestartet")
        self._log_panel.log_dim(
            "Workflow: Zertifikat wählen → Dateien wählen → "
            "SignTool konfigurieren → Signieren"
        )

    def _build_ui(self) -> None:
        """Erstellt das Haupt-Layout mit allen Panels."""
        # Hauptcontainer mit zwei Spalten: links = Konfiguration, rechts = Log
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)

        # --- Rechte Spalte: Log (ZUERST erstellen, damit Callbacks sofort funktionieren) ---
        right_frame = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(6, 12), pady=(12, 0))
        right_frame.grid_rowconfigure(0, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)

        self._log_panel = LogPanel(right_frame)
        self._log_panel.grid(row=0, column=0, sticky="nsew")

        # --- Linke Spalte: Konfiguration (scrollbar) ---
        left_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=0,
        )
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(12, 6), pady=(12, 0))

        # 1. Zertifikats-Panel
        self._cert_panel = CertPanel(
            left_frame,
            on_cert_selected=self._on_cert_selected,
            on_log=self._log_message,
        )
        self._cert_panel.pack(fill="x", pady=(0, 16))

        # Trennlinie
        ctk.CTkFrame(left_frame, height=1, fg_color="#333333").pack(
            fill="x", pady=(0, 16)
        )

        # 2. Datei-Panel
        self._file_panel = FilePanel(
            left_frame,
            on_files_changed=self._on_files_changed,
            on_log=self._log_message,
        )
        self._file_panel.pack(fill="x", pady=(0, 16))

        # Trennlinie
        ctk.CTkFrame(left_frame, height=1, fg_color="#333333").pack(
            fill="x", pady=(0, 16)
        )

        # 3. + 4. + 5. SignTool-Konfiguration & Signierung
        self._sign_panel = SignPanel(
            left_frame,
            on_log=self._log_message,
            on_status=self._set_status,
        )
        self._sign_panel.pack(fill="x", pady=(0, 12))

    def _build_statusbar(self) -> None:
        """Erstellt die Statusleiste am unteren Rand."""
        from main import APP_VERSION

        self._statusbar = ctk.CTkFrame(
            self,
            height=30,
            fg_color="#16213e",
            corner_radius=0,
        )
        self._statusbar.grid(row=1, column=0, columnspan=2, sticky="ew", padx=0, pady=0)
        self._statusbar.grid_propagate(False)

        self._status_label = ctk.CTkLabel(
            self._statusbar,
            text="Bereit",
            font=ctk.CTkFont(size=11),
            text_color="#888888",
            anchor="w",
        )
        self._status_label.pack(side="left", padx=12)

        # Info-Button (oeffnet About-Dialog)
        self._info_btn = ctk.CTkButton(
            self._statusbar,
            text="Ueber SignIT",
            width=95,
            height=22,
            font=ctk.CTkFont(size=10),
            fg_color="#1b6b3a",
            hover_color="#228b4a",
            command=self._show_about,
        )
        self._info_btn.pack(side="right", padx=(0, 12))

        # Theme-Toggle
        self._theme_btn = ctk.CTkButton(
            self._statusbar,
            text="Hell/Dunkel",
            width=80,
            height=22,
            font=ctk.CTkFont(size=10),
            fg_color="#333333",
            hover_color="#444444",
            command=self._toggle_theme,
        )
        self._theme_btn.pack(side="right", padx=(0, 6))

        # Version
        ctk.CTkLabel(
            self._statusbar,
            text=f"v{APP_VERSION}",
            font=ctk.CTkFont(size=10),
            text_color="#555555",
        ).pack(side="right", padx=(0, 8))

    def _on_cert_selected(self, cert: Optional[CertInfo]) -> None:
        """Callback wenn ein Zertifikat ausgewählt wird."""
        self._sign_panel.set_certificate(cert)

    def _on_files_changed(self, files: list) -> None:
        """Callback wenn sich die Dateiliste ändert."""
        self._sign_panel.set_files(files)

    def _log_message(self, message: str, tag: str = "") -> None:
        """Leitet Log-Nachrichten an das LogPanel weiter."""
        if hasattr(self, "_log_panel"):
            self._log_panel.log(message, tag)

    def _set_status(self, text: str) -> None:
        """Aktualisiert die Statusleiste."""
        if hasattr(self, "_status_label"):
            self._status_label.configure(text=text)

    def _show_about(self) -> None:
        """Oeffnet den 'Ueber SignIT'-Dialog."""
        from main import APP_VERSION

        AboutDialog(self, app_version=APP_VERSION)

    def _toggle_theme(self) -> None:
        """Wechselt zwischen Dark- und Light-Theme."""
        current = ctk.get_appearance_mode()
        if current == "Dark":
            ctk.set_appearance_mode("light")
        else:
            ctk.set_appearance_mode("dark")
