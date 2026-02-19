"""
Let's Do. | SignIT – Log-/Output-Panel.

Zeigt den Live-Log-Output des Signiervorgangs mit farblicher
Hervorhebung (Erfolg = grün, Fehler = rot).
"""

from __future__ import annotations

import customtkinter as ctk
from datetime import datetime


class LogPanel(ctk.CTkFrame):
    """Log-Panel mit farbigem Output für den Signiervorgang."""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.configure(fg_color="transparent")

        # --- Header ---
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=0, pady=(0, 5))

        ctk.CTkLabel(
            header,
            text="Protokoll",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(side="left")

        self._clear_btn = ctk.CTkButton(
            header,
            text="Leeren",
            width=80,
            height=28,
            font=ctk.CTkFont(size=12),
            command=self.clear,
        )
        self._clear_btn.pack(side="right")

        self._export_btn = ctk.CTkButton(
            header,
            text="Exportieren",
            width=100,
            height=28,
            font=ctk.CTkFont(size=12),
            fg_color="#555555",
            hover_color="#666666",
            command=self._export_log,
        )
        self._export_btn.pack(side="right", padx=(0, 5))

        # --- Log-Textfeld ---
        self._textbox = ctk.CTkTextbox(
            self,
            font=ctk.CTkFont(family="Consolas", size=12),
            fg_color="#1a1a2e",
            text_color="#cccccc",
            corner_radius=8,
            wrap="word",
            state="disabled",
        )
        self._textbox.pack(fill="both", expand=True)

        # Farb-Tags definieren (über das darunterliegende tk.Text-Widget)
        self._textbox._textbox.tag_configure("success", foreground="#4ade80")
        self._textbox._textbox.tag_configure("error", foreground="#f87171")
        self._textbox._textbox.tag_configure("warning", foreground="#fbbf24")
        self._textbox._textbox.tag_configure("info", foreground="#60a5fa")
        self._textbox._textbox.tag_configure("header", foreground="#c084fc")
        self._textbox._textbox.tag_configure("dim", foreground="#888888")
        self._textbox._textbox.tag_configure("timestamp", foreground="#666666")

    def _get_timestamp(self) -> str:
        """Gibt einen formatierten Zeitstempel zurück."""
        return datetime.now().strftime("[%H:%M:%S] ")

    def log(self, message: str, tag: str = "") -> None:
        """
        Fügt eine Zeile zum Log hinzu.

        Args:
            message: Die Log-Nachricht
            tag: Farb-Tag ('success', 'error', 'warning', 'info', 'header', 'dim')
        """
        self._textbox.configure(state="normal")

        # Zeitstempel einfügen
        ts = self._get_timestamp()
        self._textbox._textbox.insert("end", ts, "timestamp")

        # Nachricht einfügen
        tags = (tag,) if tag else ()
        self._textbox._textbox.insert("end", message + "\n", tags)

        self._textbox.configure(state="disabled")
        self._textbox.see("end")

    def log_success(self, message: str) -> None:
        """Erfolgs-Nachricht (grün)."""
        self.log(message, "success")

    def log_error(self, message: str) -> None:
        """Fehler-Nachricht (rot)."""
        self.log(message, "error")

    def log_warning(self, message: str) -> None:
        """Warnung (gelb)."""
        self.log(message, "warning")

    def log_info(self, message: str) -> None:
        """Info-Nachricht (blau)."""
        self.log(message, "info")

    def log_header(self, message: str) -> None:
        """Header-Nachricht (lila)."""
        self.log(message, "header")

    def log_dim(self, message: str) -> None:
        """Abgedimmte Nachricht (grau)."""
        self.log(message, "dim")

    def clear(self) -> None:
        """Löscht den gesamten Log-Inhalt."""
        self._textbox.configure(state="normal")
        self._textbox.delete("1.0", "end")
        self._textbox.configure(state="disabled")

    def _export_log(self) -> None:
        """Exportiert das Log als Textdatei."""
        from tkinter import filedialog

        content = self._textbox._textbox.get("1.0", "end-1c")
        if not content.strip():
            return

        filepath = filedialog.asksaveasfilename(
            title="Protokoll exportieren",
            defaultextension=".txt",
            filetypes=[("Textdatei", "*.txt"), ("Log-Datei", "*.log")],
            initialfile=f"signit-log-{datetime.now().strftime('%Y%m%d-%H%M%S')}.txt",
        )
        if filepath:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            self.log_info(f"Protokoll exportiert: {filepath}")

    def get_content(self) -> str:
        """Gibt den gesamten Log-Inhalt als String zurück."""
        return self._textbox._textbox.get("1.0", "end-1c")
