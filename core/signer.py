"""
Let's Do. | SignIT – SignTool-Wrapper.

Führt signtool.exe als Subprocess aus und liefert Live-Output.
"""

from __future__ import annotations

import subprocess
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List, Optional


@dataclass
class SignResult:
    """Ergebnis eines Signiervorgangs für eine einzelne Datei."""

    file_path: str
    success: bool
    return_code: int
    output: str
    error: str


class Signer:
    """
    Wrapper um signtool.exe zum Signieren von EXE-Dateien.

    Verwendung:
        signer = Signer(signtool_path="C:/path/to/signtool.exe")
        signer.sign_files(
            files=["app.exe"],
            thumbprint="AABB...",
            timestamp_url="http://timestamp.digicert.com",
            on_progress=callback,
            on_log=log_callback,
        )
    """

    def __init__(self, signtool_path: str):
        self.signtool_path = signtool_path

    def sign_file(
        self,
        file_path: str,
        thumbprint: str,
        timestamp_url: str,
        on_log: Optional[Callable[[str], None]] = None,
    ) -> SignResult:
        """
        Signiert eine einzelne Datei mit signtool.exe.

        Args:
            file_path: Pfad zur zu signierenden Datei
            thumbprint: SHA-1-Thumbprint des Zertifikats
            timestamp_url: URL des Timestamp-Servers
            on_log: Callback für Live-Log-Output (optional)

        Returns:
            SignResult mit Erfolg/Fehler-Information
        """
        cmd = [
            self.signtool_path,
            "sign",
            "/sha1",
            thumbprint,
            "/tr",
            timestamp_url,
            "/td",
            "sha256",
            "/fd",
            "sha256",
            file_path,
        ]

        if on_log:
            on_log(f"Befehl: {' '.join(cmd)}")

        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )

            stdout_lines: list[str] = []
            stderr_lines: list[str] = []

            # FIX #1: stdout/stderr parallel lesen, um Pipe-Deadlocks zu vermeiden.
            def _read_stream(stream, target: list[str], is_error: bool = False) -> None:
                try:
                    for line in iter(stream.readline, ""):
                        line = line.rstrip("\n\r")
                        if line:
                            target.append(line)
                            if on_log:
                                on_log(
                                    f"  [FEHLER] {line}" if is_error else f"  {line}"
                                )
                finally:
                    stream.close()

            threads: list[threading.Thread] = []
            if process.stdout:
                t_out = threading.Thread(
                    target=_read_stream,
                    args=(process.stdout, stdout_lines, False),
                    daemon=True,
                )
                threads.append(t_out)
                t_out.start()

            if process.stderr:
                t_err = threading.Thread(
                    target=_read_stream,
                    args=(process.stderr, stderr_lines, True),
                    daemon=True,
                )
                threads.append(t_err)
                t_err.start()

            process.wait()
            for t in threads:
                t.join()

            return SignResult(
                file_path=file_path,
                success=(process.returncode == 0),
                return_code=process.returncode,
                output="\n".join(stdout_lines),
                error="\n".join(stderr_lines),
            )

        except FileNotFoundError:
            msg = f"signtool.exe nicht gefunden: {self.signtool_path}"
            if on_log:
                on_log(f"  [FEHLER] {msg}")
            return SignResult(
                file_path=file_path,
                success=False,
                return_code=-1,
                output="",
                error=msg,
            )
        except Exception as e:
            msg = f"Unerwarteter Fehler: {e}"
            if on_log:
                on_log(f"  [FEHLER] {msg}")
            return SignResult(
                file_path=file_path,
                success=False,
                return_code=-1,
                output="",
                error=msg,
            )

    def sign_files(
        self,
        files: List[str],
        thumbprint: str,
        timestamp_url: str,
        on_progress: Optional[Callable[[int, int, str], None]] = None,
        on_log: Optional[Callable[[str], None]] = None,
        on_result: Optional[Callable[[SignResult], None]] = None,
        on_complete: Optional[Callable[[List[SignResult]], None]] = None,
    ) -> None:
        """
        Signiert mehrere Dateien sequentiell in einem Hintergrund-Thread.

        Args:
            files: Liste der Dateipfade
            thumbprint: SHA-1-Thumbprint
            timestamp_url: Timestamp-Server-URL
            on_progress: Callback(current, total, filename) für Fortschritt
            on_log: Callback(message) für Log-Zeilen
            on_result: Callback(SignResult) nach jeder Datei
            on_complete: Callback(List[SignResult]) wenn alles fertig
        """

        def _worker():
            results: List[SignResult] = []
            total = len(files)

            for idx, file_path in enumerate(files, start=1):
                filename = Path(file_path).name
                if on_progress:
                    on_progress(idx, total, filename)
                if on_log:
                    on_log(f"\n[{idx}/{total}] Signiere: {filename}")

                result = self.sign_file(
                    file_path=file_path,
                    thumbprint=thumbprint,
                    timestamp_url=timestamp_url,
                    on_log=on_log,
                )
                results.append(result)

                if on_result:
                    on_result(result)

                if result.success:
                    if on_log:
                        on_log(f"  -> Erfolgreich signiert!")
                else:
                    if on_log:
                        on_log(f"  -> FEHLER (Code: {result.return_code})")

            if on_complete:
                on_complete(results)

        thread = threading.Thread(target=_worker, daemon=True)
        thread.start()
