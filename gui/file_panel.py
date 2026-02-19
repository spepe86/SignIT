"""
Let's Do. | SignIT – Datei-Auswahl-Panel.

Ermöglicht die Auswahl von EXE-Dateien zum Signieren.
Unterstützt Mehrfachauswahl, Drag-and-Drop-ähnliche UX,
und Entfernen einzelner Dateien.
"""

from __future__ import annotations

import os
from pathlib import Path
from tkinter import filedialog
from typing import Callable, List, Optional

import customtkinter as ctk

from core.utils import format_file_size


class FilePanel(ctk.CTkFrame):
    """Panel zur Auswahl und Verwaltung der zu signierenden Dateien."""

    def __init__(
        self,
        master,
        on_files_changed: Optional[Callable[[List[str]], None]] = None,
        on_log: Optional[Callable[[str, str], None]] = None,
        **kwargs,
    ):
        super().__init__(master, **kwargs)
        self.configure(fg_color="transparent")

        self._on_files_changed = on_files_changed
        self._on_log = on_log
        self._files: List[str] = []
        self._file_frames: List[ctk.CTkFrame] = []

        # --- Header ---
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=0, pady=(0, 8))

        ctk.CTkLabel(
            header,
            text="2. Dateien auswaehlen",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(side="left")

        # --- Buttons ---
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=0, pady=(0, 8))

        self._add_btn = ctk.CTkButton(
            btn_frame,
            text="Dateien hinzufuegen...",
            width=170,
            height=32,
            font=ctk.CTkFont(size=13),
            command=self._browse_files,
        )
        self._add_btn.pack(side="left")

        self._clear_btn = ctk.CTkButton(
            btn_frame,
            text="Alle entfernen",
            width=130,
            height=32,
            font=ctk.CTkFont(size=13),
            fg_color="#555555",
            hover_color="#666666",
            command=self._clear_files,
        )
        self._clear_btn.pack(side="left", padx=(8, 0))

        self._count_label = ctk.CTkLabel(
            btn_frame,
            text="Keine Dateien ausgewählt",
            font=ctk.CTkFont(size=12),
            text_color="#888888",
        )
        self._count_label.pack(side="right")

        # --- Dateiliste (scrollbar) ---
        self._scroll_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="#1a1a2e",
            corner_radius=8,
            height=140,
        )
        self._scroll_frame.pack(fill="both", expand=True)

        # Platzhalter
        self._placeholder = ctk.CTkLabel(
            self._scroll_frame,
            text='Klicken Sie "Dateien hinzufügen" oder ziehen Sie Dateien hierher...',
            font=ctk.CTkFont(size=13),
            text_color="#666666",
        )
        self._placeholder.pack(pady=30)

    def _browse_files(self) -> None:
        """Öffnet den Datei-Dialog für Mehrfachauswahl."""
        filepaths = filedialog.askopenfilenames(
            title="EXE-Dateien zum Signieren auswählen",
            filetypes=[
                ("Ausführbare Dateien", "*.exe"),
                ("DLL-Dateien", "*.dll"),
                ("MSI-Dateien", "*.msi"),
                ("Alle signierbaren Dateien", "*.exe;*.dll;*.msi;*.sys;*.ocx;*.cab"),
                ("Alle Dateien", "*.*"),
            ],
        )
        if filepaths:
            self._add_files(list(filepaths))

    def _add_files(self, new_files: List[str]) -> None:
        """Fügt neue Dateien zur Liste hinzu (ohne Duplikate)."""
        added = 0
        for fp in new_files:
            norm = os.path.normpath(fp)
            if norm not in self._files:
                self._files.append(norm)
                added += 1

        if added > 0:
            self._refresh_file_list()
            if self._on_log:
                self._on_log(
                    f"{added} Datei(en) hinzugefügt. Gesamt: {len(self._files)}",
                    "info",
                )
            if self._on_files_changed:
                self._on_files_changed(self._files.copy())

    def _remove_file(self, filepath: str) -> None:
        """Entfernt eine einzelne Datei aus der Liste."""
        if filepath in self._files:
            self._files.remove(filepath)
            self._refresh_file_list()
            if self._on_log:
                self._on_log(f"Datei entfernt: {Path(filepath).name}", "dim")
            if self._on_files_changed:
                self._on_files_changed(self._files.copy())

    def _clear_files(self) -> None:
        """Entfernt alle Dateien aus der Liste."""
        if not self._files:
            return
        self._files.clear()
        self._refresh_file_list()
        if self._on_log:
            self._on_log("Alle Dateien entfernt.", "dim")
        if self._on_files_changed:
            self._on_files_changed(self._files.copy())

    def _refresh_file_list(self) -> None:
        """Aktualisiert die angezeigte Dateiliste."""
        # Alte Einträge löschen
        for f in self._file_frames:
            f.destroy()
        self._file_frames.clear()

        if self._placeholder:
            self._placeholder.destroy()
            self._placeholder = None

        if not self._files:
            self._count_label.configure(text="Keine Dateien ausgewählt")
            self._placeholder = ctk.CTkLabel(
                self._scroll_frame,
                text='Klicken Sie "Dateien hinzufügen" oder ziehen Sie Dateien hierher...',
                font=ctk.CTkFont(size=13),
                text_color="#666666",
            )
            self._placeholder.pack(pady=30)
            return

        self._count_label.configure(text=f"{len(self._files)} Datei(en) ausgewählt")

        for filepath in self._files:
            frame = self._create_file_row(filepath)
            self._file_frames.append(frame)

    def _create_file_row(self, filepath: str) -> ctk.CTkFrame:
        """Erstellt eine Zeile für eine Datei in der Liste."""
        frame = ctk.CTkFrame(
            self._scroll_frame,
            fg_color="#0f3460",
            corner_radius=4,
            height=36,
        )
        frame.pack(fill="x", padx=2, pady=1)
        frame.pack_propagate(False)

        # Dateiname
        name = Path(filepath).name
        ctk.CTkLabel(
            frame,
            text=f"  {name}",
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w",
        ).pack(side="left", padx=(4, 0))

        # Pfad (gekürzt)
        dir_path = str(Path(filepath).parent)
        if len(dir_path) > 50:
            dir_path = "..." + dir_path[-47:]
        ctk.CTkLabel(
            frame,
            text=dir_path,
            font=ctk.CTkFont(size=11),
            text_color="#888888",
            anchor="w",
        ).pack(side="left", padx=(8, 0))

        # Dateigröße
        try:
            size = os.path.getsize(filepath)
            size_text = format_file_size(size)
        except OSError:
            size_text = "?"
        ctk.CTkLabel(
            frame,
            text=size_text,
            font=ctk.CTkFont(size=11),
            text_color="#aaaaaa",
        ).pack(side="right", padx=(0, 8))

        # Entfernen-Button
        remove_btn = ctk.CTkButton(
            frame,
            text="X",
            width=28,
            height=24,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#662222",
            hover_color="#883333",
            command=lambda fp=filepath: self._remove_file(fp),
        )
        remove_btn.pack(side="right", padx=(0, 4))

        return frame

    @property
    def files(self) -> List[str]:
        """Gibt die Liste der ausgewählten Dateien zurück."""
        return self._files.copy()
