"""
Let's Do. | SignIT – Zertifikats-Auswahl-Panel.

Zeigt verfügbare Code-Signing-Zertifikate in einer Tabelle
und ermöglicht die Auswahl eines Zertifikats zum Signieren.
"""

from __future__ import annotations

import threading
from typing import Callable, List, Optional

import customtkinter as ctk

from core.certstore import CertInfo, get_certificates


class CertPanel(ctk.CTkFrame):
    """Panel zur Auswahl eines Code-Signing-Zertifikats."""

    def __init__(
        self,
        master,
        on_cert_selected: Optional[Callable[[Optional[CertInfo]], None]] = None,
        on_log: Optional[Callable[[str, str], None]] = None,
        **kwargs,
    ):
        super().__init__(master, **kwargs)
        self.configure(fg_color="transparent")

        self._on_cert_selected = on_cert_selected
        self._on_log = on_log
        self._certs: List[CertInfo] = []
        self._selected_cert: Optional[CertInfo] = None
        self._cert_frames: List[ctk.CTkFrame] = []

        # --- Header-Bereich ---
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=0, pady=(0, 8))

        ctk.CTkLabel(
            header,
            text="1. Zertifikat auswaehlen",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(side="left")

        # --- Steuerungsbereich ---
        controls = ctk.CTkFrame(self, fg_color="transparent")
        controls.pack(fill="x", padx=0, pady=(0, 8))

        ctk.CTkLabel(
            controls,
            text="Speicherort:",
            font=ctk.CTkFont(size=13),
        ).pack(side="left", padx=(0, 8))

        self._store_var = ctk.StringVar(value="CurrentUser")
        self._store_menu = ctk.CTkSegmentedButton(
            controls,
            values=["CurrentUser", "LocalMachine"],
            variable=self._store_var,
            command=self._on_store_changed,
            font=ctk.CTkFont(size=12),
        )
        self._store_menu.pack(side="left", padx=(0, 12))

        self._refresh_btn = ctk.CTkButton(
            controls,
            text="Aktualisieren",
            width=120,
            height=30,
            font=ctk.CTkFont(size=12),
            command=self.load_certificates,
        )
        self._refresh_btn.pack(side="left")

        self._status_label = ctk.CTkLabel(
            controls,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="#888888",
        )
        self._status_label.pack(side="right")

        # --- Zertifikatsliste (scrollbar) ---
        self._scroll_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="#1a1a2e",
            corner_radius=8,
            height=180,
        )
        self._scroll_frame.pack(fill="both", expand=True)

        # Spaltenüberschriften
        self._header_frame = ctk.CTkFrame(
            self._scroll_frame, fg_color="#16213e", corner_radius=4
        )
        self._header_frame.pack(fill="x", padx=2, pady=(2, 4))
        self._header_frame.columnconfigure(0, weight=3)
        self._header_frame.columnconfigure(1, weight=2)
        self._header_frame.columnconfigure(2, weight=1)
        self._header_frame.columnconfigure(3, weight=2)

        for col, text in enumerate(
            ["Subject", "Aussteller", "Gueltig bis", "Thumbprint"]
        ):
            ctk.CTkLabel(
                self._header_frame,
                text=text,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color="#a0a0a0",
                anchor="w",
            ).grid(row=0, column=col, sticky="w", padx=8, pady=4)

        # Platzhalter-Text
        self._placeholder = ctk.CTkLabel(
            self._scroll_frame,
            text='Klicken Sie "Aktualisieren" um Zertifikate zu laden...',
            font=ctk.CTkFont(size=13),
            text_color="#666666",
        )
        self._placeholder.pack(pady=30)

    def _on_store_changed(self, value: str) -> None:
        """Wird aufgerufen, wenn der Store-Ort gewechselt wird."""
        self.load_certificates()

    def load_certificates(self) -> None:
        """Lädt Zertifikate im Hintergrund-Thread."""
        # FIX #3: Store-Wert im UI-Thread lesen und an Worker übergeben (Tk-Thread-Safety).
        store = self._store_var.get()
        self._refresh_btn.configure(state="disabled", text="Lade...")
        self._status_label.configure(text="Lade Zertifikate...", text_color="#fbbf24")
        self._clear_cert_list()

        if self._on_log:
            self._on_log(f"Lade Zertifikate aus Speicher: {store}\\My ...", "info")

        def _load(selected_store: str):
            try:
                certs = get_certificates(selected_store)
                self.after(0, lambda: self._display_certificates(certs))
            except Exception as e:
                self.after(0, lambda: self._show_error(str(e)))

        thread = threading.Thread(target=_load, args=(store,), daemon=True)
        thread.start()

    def _display_certificates(self, certs: List[CertInfo]) -> None:
        """Zeigt die geladenen Zertifikate in der Liste an."""
        self._certs = certs
        self._refresh_btn.configure(state="normal", text="Aktualisieren")

        if self._placeholder:
            self._placeholder.destroy()
            self._placeholder = None

        self._clear_cert_list()

        if not certs:
            no_certs = ctk.CTkLabel(
                self._scroll_frame,
                text="Keine gültigen Zertifikate mit privatem Schlüssel gefunden.",
                font=ctk.CTkFont(size=13),
                text_color="#f87171",
            )
            no_certs.pack(pady=30)
            self._cert_frames.append(no_certs)
            self._status_label.configure(
                text="Keine Zertifikate gefunden", text_color="#f87171"
            )
            if self._on_log:
                self._on_log("Keine gültigen Zertifikate gefunden.", "warning")
            return

        self._status_label.configure(
            text=f"{len(certs)} Zertifikat(e) gefunden",
            text_color="#4ade80",
        )
        if self._on_log:
            self._on_log(f"{len(certs)} Zertifikat(e) gefunden.", "success")

        for cert in certs:
            frame = self._create_cert_row(cert)
            self._cert_frames.append(frame)

    def _create_cert_row(self, cert: CertInfo) -> ctk.CTkFrame:
        """Erstellt eine Zeile in der Zertifikatsliste."""
        frame = ctk.CTkFrame(
            self._scroll_frame,
            fg_color="#0f3460",
            corner_radius=4,
            cursor="hand2",
        )
        frame.pack(fill="x", padx=2, pady=1)
        frame.columnconfigure(0, weight=3)
        frame.columnconfigure(1, weight=2)
        frame.columnconfigure(2, weight=1)
        frame.columnconfigure(3, weight=2)

        # Hover-Effekt manuell (CTkFrame hat kein hover_color)
        frame._is_selected = False  # type: ignore[attr-defined]

        def _on_enter(e, f=frame):
            if not f._is_selected:  # type: ignore[attr-defined]
                f.configure(fg_color="#1a4a7a")

        def _on_leave(e, f=frame):
            if not f._is_selected:  # type: ignore[attr-defined]
                f.configure(fg_color="#0f3460")

        frame.bind("<Enter>", _on_enter)
        frame.bind("<Leave>", _on_leave)

        # Subject
        ctk.CTkLabel(
            frame,
            text=cert.subject[:40] + ("..." if len(cert.subject) > 40 else ""),
            font=ctk.CTkFont(size=12),
            anchor="w",
        ).grid(row=0, column=0, sticky="w", padx=8, pady=6)

        # Issuer
        ctk.CTkLabel(
            frame,
            text=cert.issuer[:30] + ("..." if len(cert.issuer) > 30 else ""),
            font=ctk.CTkFont(size=12),
            text_color="#aaaaaa",
            anchor="w",
        ).grid(row=0, column=1, sticky="w", padx=8, pady=6)

        # Gueltig bis
        ctk.CTkLabel(
            frame,
            text=cert.not_after_str,
            font=ctk.CTkFont(size=12),
            text_color="#aaaaaa",
            anchor="w",
        ).grid(row=0, column=2, sticky="w", padx=8, pady=6)

        # Thumbprint (gekuerzt)
        tp_short = cert.thumbprint[:16] + "..."
        ctk.CTkLabel(
            frame,
            text=tp_short,
            font=ctk.CTkFont(family="Consolas", size=11),
            text_color="#888888",
            anchor="w",
        ).grid(row=0, column=3, sticky="w", padx=8, pady=6)

        # Klick-Event auf den gesamten Frame + alle Kinder
        frame.bind("<Button-1>", lambda e, c=cert, f=frame: self._select_cert(c, f))
        for child in frame.winfo_children():
            child.bind("<Button-1>", lambda e, c=cert, f=frame: self._select_cert(c, f))
            child.bind("<Enter>", _on_enter)
            child.bind("<Leave>", _on_leave)

        return frame

    def _select_cert(self, cert: CertInfo, frame: ctk.CTkFrame) -> None:
        """Markiert ein Zertifikat als ausgewaehlt."""
        # Alle Frames zuruecksetzen
        for f in self._cert_frames:
            if isinstance(f, ctk.CTkFrame) and hasattr(f, "configure"):
                try:
                    f.configure(fg_color="#0f3460")
                    f._is_selected = False  # type: ignore[attr-defined]
                except Exception:
                    pass

        # Ausgewaehlten Frame hervorheben
        frame.configure(fg_color="#1b6b3a")
        frame._is_selected = True  # type: ignore[attr-defined]
        self._selected_cert = cert

        if self._on_log:
            self._on_log(
                f"Zertifikat ausgewählt: {cert.subject} ({cert.thumbprint[:16]}...)",
                "info",
            )

        if self._on_cert_selected:
            self._on_cert_selected(cert)

    def _clear_cert_list(self) -> None:
        """Entfernt alle Zertifikats-Einträge aus der Liste."""
        for f in self._cert_frames:
            f.destroy()
        self._cert_frames.clear()
        self._selected_cert = None

    def _show_error(self, message: str) -> None:
        """Zeigt eine Fehlermeldung an."""
        self._refresh_btn.configure(state="normal", text="Aktualisieren")
        self._status_label.configure(text="Fehler beim Laden", text_color="#f87171")

        if self._on_log:
            self._on_log(f"Fehler beim Laden der Zertifikate: {message}", "error")

        error_label = ctk.CTkLabel(
            self._scroll_frame,
            text=f"Fehler: {message}",
            font=ctk.CTkFont(size=13),
            text_color="#f87171",
            wraplength=600,
        )
        error_label.pack(pady=20)
        self._cert_frames.append(error_label)

    @property
    def selected_cert(self) -> Optional[CertInfo]:
        """Gibt das aktuell ausgewählte Zertifikat zurück."""
        return self._selected_cert
