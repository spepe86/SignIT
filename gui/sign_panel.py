"""
Let's Do. | SignIT – Signier-Konfiguration & Ausführung.

Enthält SignTool-Pfad-Konfiguration, Timestamp-Server-Einstellung,
Fortschrittsanzeige und den Start-Button für den Signiervorgang.
"""

from __future__ import annotations

import os
from pathlib import Path
from tkinter import filedialog, messagebox
from typing import Callable, List, Optional

import customtkinter as ctk

from core.certstore import CertInfo
from core.signer import Signer, SignResult
from core.utils import (
    TIMESTAMP_SERVERS,
    find_signtool,
    find_signtool_in_windows_kits,
    validate_signtool,
)


class SignPanel(ctk.CTkFrame):
    """
    Panel für SignTool-Konfiguration, Timestamp-Einstellung
    und Ausführung des Signiervorgangs.
    """

    def __init__(
        self,
        master,
        on_log: Optional[Callable[[str, str], None]] = None,
        on_status: Optional[Callable[[str], None]] = None,
        **kwargs,
    ):
        super().__init__(master, **kwargs)
        self.configure(fg_color="transparent")

        self._on_log = on_log
        self._on_status = on_status
        self._selected_cert: Optional[CertInfo] = None
        self._files: List[str] = []
        self._is_signing = False

        # ===================================================================
        # Abschnitt: SignTool-Pfad
        # ===================================================================
        signtool_section = ctk.CTkFrame(self, fg_color="transparent")
        signtool_section.pack(fill="x", padx=0, pady=(0, 12))

        ctk.CTkLabel(
            signtool_section,
            text="3. SignTool-Pfad",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(anchor="w")

        signtool_row = ctk.CTkFrame(signtool_section, fg_color="transparent")
        signtool_row.pack(fill="x", pady=(4, 0))

        self._signtool_entry = ctk.CTkEntry(
            signtool_row,
            placeholder_text="Pfad zu signtool.exe (wird automatisch gesucht)...",
            font=ctk.CTkFont(size=12),
            height=34,
        )
        self._signtool_entry.pack(side="left", fill="x", expand=True)

        self._browse_signtool_btn = ctk.CTkButton(
            signtool_row,
            text="Durchsuchen...",
            width=120,
            height=34,
            font=ctk.CTkFont(size=12),
            command=self._browse_signtool,
        )
        self._browse_signtool_btn.pack(side="left", padx=(6, 0))

        self._auto_find_btn = ctk.CTkButton(
            signtool_row,
            text="Auto-Suche",
            width=100,
            height=34,
            font=ctk.CTkFont(size=12),
            fg_color="#555555",
            hover_color="#666666",
            command=self._auto_find_signtool,
        )
        self._auto_find_btn.pack(side="left", padx=(6, 0))

        self._signtool_status = ctk.CTkLabel(
            signtool_section,
            text="",
            font=ctk.CTkFont(size=11),
            text_color="#888888",
        )
        self._signtool_status.pack(anchor="w", pady=(2, 0))

        # ===================================================================
        # Abschnitt: Timestamp-Server
        # ===================================================================
        ts_section = ctk.CTkFrame(self, fg_color="transparent")
        ts_section.pack(fill="x", padx=0, pady=(0, 12))

        ctk.CTkLabel(
            ts_section,
            text="4. Timestamp-Server",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(anchor="w")

        ts_row = ctk.CTkFrame(ts_section, fg_color="transparent")
        ts_row.pack(fill="x", pady=(4, 0))

        # Vorauswahl-Dropdown
        ts_names = [name for name, _ in TIMESTAMP_SERVERS]
        self._ts_dropdown = ctk.CTkComboBox(
            ts_row,
            values=ts_names,
            font=ctk.CTkFont(size=12),
            width=220,
            height=34,
            command=self._on_ts_selected,
        )
        self._ts_dropdown.set(ts_names[0])
        self._ts_dropdown.pack(side="left")

        self._ts_entry = ctk.CTkEntry(
            ts_row,
            font=ctk.CTkFont(size=12),
            height=34,
        )
        self._ts_entry.pack(side="left", fill="x", expand=True, padx=(8, 0))
        self._ts_entry.insert(0, TIMESTAMP_SERVERS[0][1])

        # ===================================================================
        # Abschnitt: Signieren
        # ===================================================================
        sign_section = ctk.CTkFrame(self, fg_color="transparent")
        sign_section.pack(fill="x", padx=0, pady=(0, 8))

        ctk.CTkLabel(
            sign_section,
            text="5. Signieren",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(anchor="w")

        # Zusammenfassung
        self._summary_frame = ctk.CTkFrame(
            sign_section, fg_color="#16213e", corner_radius=8
        )
        self._summary_frame.pack(fill="x", pady=(4, 8))

        self._summary_cert = ctk.CTkLabel(
            self._summary_frame,
            text="Zertifikat: (nicht ausgewählt)",
            font=ctk.CTkFont(size=12),
            text_color="#aaaaaa",
            anchor="w",
        )
        self._summary_cert.pack(anchor="w", padx=12, pady=(8, 2))

        self._summary_files = ctk.CTkLabel(
            self._summary_frame,
            text="Dateien: (keine ausgewählt)",
            font=ctk.CTkFont(size=12),
            text_color="#aaaaaa",
            anchor="w",
        )
        self._summary_files.pack(anchor="w", padx=12, pady=(2, 8))

        # Fortschrittsbalken
        self._progress_bar = ctk.CTkProgressBar(
            sign_section,
            height=8,
            corner_radius=4,
        )
        self._progress_bar.pack(fill="x", pady=(0, 4))
        self._progress_bar.set(0)

        self._progress_label = ctk.CTkLabel(
            sign_section,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="#888888",
        )
        self._progress_label.pack(anchor="w")

        # Sign-Button
        self._sign_btn = ctk.CTkButton(
            sign_section,
            text="Jetzt signieren",
            width=200,
            height=42,
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color="#1b6b3a",
            hover_color="#228b4a",
            command=self._start_signing,
        )
        self._sign_btn.pack(pady=(8, 0))

        # --- Automatisch signtool suchen ---
        self._auto_find_signtool()

    def _browse_signtool(self) -> None:
        """Öffnet einen Datei-Dialog für signtool.exe."""
        filepath = filedialog.askopenfilename(
            title="signtool.exe auswählen",
            filetypes=[("SignTool", "signtool.exe"), ("Alle Dateien", "*.*")],
        )
        if filepath:
            self._signtool_entry.delete(0, "end")
            self._signtool_entry.insert(0, filepath)
            self._validate_signtool_path(filepath)

    def _auto_find_signtool(self) -> None:
        """Sucht automatisch nach signtool.exe."""
        if self._on_log:
            self._on_log("Suche signtool.exe...", "info")

        result = find_signtool()
        if result:
            self._signtool_entry.delete(0, "end")
            self._signtool_entry.insert(0, result)
            self._validate_signtool_path(result)
            if self._on_log:
                self._on_log(f"signtool.exe gefunden: {result}", "success")
        else:
            self._signtool_status.configure(
                text="signtool.exe nicht gefunden. Bitte manuell angeben.",
                text_color="#f87171",
            )
            if self._on_log:
                self._on_log(
                    "signtool.exe nicht gefunden. Bitte installieren Sie das Windows SDK "
                    "oder geben Sie den Pfad manuell an.",
                    "warning",
                )

            # Zeige gefundene Pfade als Hilfe
            found = find_signtool_in_windows_kits()
            if found:
                if self._on_log:
                    self._on_log(f"Mögliche Pfade: {', '.join(found[:3])}", "dim")

    def _validate_signtool_path(self, path: str) -> bool:
        """Validiert den signtool-Pfad und aktualisiert den Status."""
        if validate_signtool(path):
            self._signtool_status.configure(
                text=f"Gefunden: {path}",
                text_color="#4ade80",
            )
            return True
        else:
            self._signtool_status.configure(
                text="Ungültiger Pfad – signtool.exe nicht gefunden!",
                text_color="#f87171",
            )
            return False

    def _on_ts_selected(self, choice: str) -> None:
        """Aktualisiert die URL beim Wechsel des Timestamp-Servers."""
        for name, url in TIMESTAMP_SERVERS:
            if name == choice:
                self._ts_entry.delete(0, "end")
                self._ts_entry.insert(0, url)
                break

    def set_certificate(self, cert: Optional[CertInfo]) -> None:
        """Setzt das ausgewählte Zertifikat (von CertPanel aufgerufen)."""
        self._selected_cert = cert
        if cert:
            self._summary_cert.configure(
                text=f"Zertifikat: {cert.subject}  [{cert.thumbprint[:16]}...]",
                text_color="#4ade80",
            )
        else:
            self._summary_cert.configure(
                text="Zertifikat: (nicht ausgewählt)",
                text_color="#aaaaaa",
            )

    def set_files(self, files: List[str]) -> None:
        """Setzt die Dateiliste (von FilePanel aufgerufen)."""
        self._files = files
        count = len(files)
        if count > 0:
            self._summary_files.configure(
                text=f"Dateien: {count} Datei(en) ausgewählt",
                text_color="#4ade80",
            )
        else:
            self._summary_files.configure(
                text="Dateien: (keine ausgewählt)",
                text_color="#aaaaaa",
            )

    def _start_signing(self) -> None:
        """Startet den Signiervorgang mit Validierung."""
        if self._is_signing:
            return

        # --- Validierung ---
        signtool_path = self._signtool_entry.get().strip()
        if not signtool_path or not validate_signtool(signtool_path):
            messagebox.showwarning(
                "SignTool fehlt",
                "Bitte geben Sie einen gültigen Pfad zu signtool.exe an.",
            )
            return

        if not self._selected_cert:
            messagebox.showwarning(
                "Kein Zertifikat",
                "Bitte wählen Sie ein Zertifikat aus der Liste aus.",
            )
            return

        if not self._files:
            messagebox.showwarning(
                "Keine Dateien",
                "Bitte wählen Sie mindestens eine Datei zum Signieren aus.",
            )
            return

        ts_url = self._ts_entry.get().strip()
        if not ts_url:
            messagebox.showwarning(
                "Timestamp-Server",
                "Bitte geben Sie eine Timestamp-Server-URL an.",
            )
            return

        # --- Bestätigung ---
        count = len(self._files)
        confirm = messagebox.askyesno(
            "Signierung starten",
            f"Möchten Sie {count} Datei(en) mit dem Zertifikat\n"
            f"'{self._selected_cert.subject}'\n"
            f"signieren?",
        )
        if not confirm:
            return

        # --- Signierung starten ---
        self._is_signing = True
        self._sign_btn.configure(state="disabled", text="Signiere...")
        self._progress_bar.set(0)
        self._progress_label.configure(text="Starte Signiervorgang...")

        if self._on_log:
            self._on_log("=" * 60, "header")
            self._on_log("SIGNIERVORGANG GESTARTET", "header")
            self._on_log(f"Zertifikat: {self._selected_cert.subject}", "info")
            self._on_log(f"Thumbprint: {self._selected_cert.thumbprint}", "dim")
            self._on_log(f"Timestamp:  {ts_url}", "dim")
            self._on_log(f"Dateien:    {count}", "dim")
            self._on_log("=" * 60, "header")

        if self._on_status:
            self._on_status("Signiere...")

        signer = Signer(signtool_path)

        def _on_progress(current: int, total: int, filename: str):
            self.after(0, lambda: self._update_progress(current, total, filename))

        def _on_log_line(msg: str):
            # Automatische Farb-Erkennung
            tag = ""
            if "[FEHLER]" in msg:
                tag = "error"
            # FIX #4: Case-insensitive Erfolgsprüfung korrekt auf lower()-String anwenden.
            elif "Erfolgreich" in msg or "successfully" in msg.lower():
                tag = "success"
            elif "Signiere:" in msg:
                tag = "info"
            elif "Befehl:" in msg:
                tag = "dim"

            if self._on_log:
                self.after(0, lambda: self._on_log(msg, tag))

        def _on_result(result: SignResult):
            pass  # Wird über on_log abgedeckt

        def _on_complete(results: List[SignResult]):
            self.after(0, lambda: self._signing_complete(results))

        signer.sign_files(
            files=self._files,
            thumbprint=self._selected_cert.thumbprint,
            timestamp_url=ts_url,
            on_progress=_on_progress,
            on_log=_on_log_line,
            on_result=_on_result,
            on_complete=_on_complete,
        )

    def _update_progress(self, current: int, total: int, filename: str) -> None:
        """Aktualisiert die Fortschrittsanzeige."""
        progress = current / total
        self._progress_bar.set(progress)
        self._progress_label.configure(
            text=f"[{current}/{total}] {filename}",
        )
        if self._on_status:
            self._on_status(f"Signiere [{current}/{total}]: {filename}")

    def _signing_complete(self, results: List[SignResult]) -> None:
        """Wird nach Abschluss des Signiervorgangs aufgerufen."""
        self._is_signing = False
        self._sign_btn.configure(state="normal", text="Jetzt signieren")

        success = sum(1 for r in results if r.success)
        failed = sum(1 for r in results if not r.success)
        total = len(results)

        self._progress_bar.set(1.0)

        if failed == 0:
            self._progress_label.configure(
                text=f"Alle {total} Datei(en) erfolgreich signiert!",
                text_color="#4ade80",
            )
            if self._on_log:
                self._on_log("=" * 60, "header")
                self._on_log(
                    f"ERGEBNIS: {success}/{total} erfolgreich signiert",
                    "success",
                )
                self._on_log("=" * 60, "header")
            if self._on_status:
                self._on_status(f"Fertig - {success}/{total} erfolgreich")
        else:
            self._progress_label.configure(
                text=f"{success} erfolgreich, {failed} fehlgeschlagen von {total}",
                text_color="#fbbf24" if success > 0 else "#f87171",
            )
            if self._on_log:
                self._on_log("=" * 60, "header")
                self._on_log(
                    f"ERGEBNIS: {success} erfolgreich, {failed} fehlgeschlagen",
                    "error" if success == 0 else "warning",
                )
                for r in results:
                    if not r.success:
                        self._on_log(
                            f"  FEHLER: {Path(r.file_path).name} – {r.error}", "error"
                        )
                self._on_log("=" * 60, "header")
            if self._on_status:
                self._on_status(f"Fertig - {failed} Fehler")
