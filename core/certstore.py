"""
Let's Do. | SignIT – Windows-Zertifikatsspeicher-Zugriff.

Liest Code-Signing-Zertifikate aus dem Windows Certificate Store
über ctypes/Win32-API oder PowerShell-Fallback.
"""

from __future__ import annotations

import ctypes
import ctypes.wintypes as wt
import subprocess
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List, Optional


# ---------------------------------------------------------------------------
# Datenklasse für ein Zertifikat
# ---------------------------------------------------------------------------
@dataclass
class CertInfo:
    """Repräsentiert ein Zertifikat aus dem Windows-Speicher."""

    subject: str
    issuer: str
    thumbprint: str
    not_after: datetime
    has_private_key: bool

    @property
    def not_after_str(self) -> str:
        """Formatiertes Ablaufdatum."""
        return self.not_after.strftime("%d.%m.%Y %H:%M")

    @property
    def is_valid(self) -> bool:
        """Prüft, ob das Zertifikat noch gültig ist."""
        return self.not_after > datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# Win32-API-Konstanten & -Strukturen
# ---------------------------------------------------------------------------
CERT_STORE_PROV_SYSTEM = 10
CERT_SYSTEM_STORE_CURRENT_USER = 0x00010000
CERT_SYSTEM_STORE_LOCAL_MACHINE = 0x00020000
X509_ASN_ENCODING = 0x00000001
PKCS_7_ASN_ENCODING = 0x00010000
ENCODING = X509_ASN_ENCODING | PKCS_7_ASN_ENCODING
CERT_FIND_ANY = 0

# CertNameString-Typen
CERT_NAME_SIMPLE_DISPLAY_TYPE = 4
CERT_NAME_ISSUER_FLAG = 0x1


class CRYPT_DATA_BLOB(ctypes.Structure):
    _fields_ = [
        ("cbData", wt.DWORD),
        ("pbData", ctypes.POINTER(ctypes.c_byte)),
    ]


class CRYPT_BIT_BLOB(ctypes.Structure):
    _fields_ = [
        ("cbData", wt.DWORD),
        ("pbData", ctypes.POINTER(ctypes.c_byte)),
        ("cUnusedBits", wt.DWORD),
    ]


class CRYPT_ALGORITHM_IDENTIFIER(ctypes.Structure):
    _fields_ = [
        ("pszObjId", ctypes.c_char_p),
        ("Parameters", CRYPT_DATA_BLOB),
    ]


class CERT_PUBLIC_KEY_INFO(ctypes.Structure):
    _fields_ = [
        ("Algorithm", CRYPT_ALGORITHM_IDENTIFIER),
        ("PublicKey", CRYPT_BIT_BLOB),
    ]


class FILETIME(ctypes.Structure):
    _fields_ = [
        ("dwLowDateTime", wt.DWORD),
        ("dwHighDateTime", wt.DWORD),
    ]


class CERT_INFO(ctypes.Structure):
    _fields_ = [
        ("dwVersion", wt.DWORD),
        ("SerialNumber", CRYPT_DATA_BLOB),
        ("SignatureAlgorithm", CRYPT_ALGORITHM_IDENTIFIER),
        ("Issuer", CRYPT_DATA_BLOB),
        ("NotBefore", FILETIME),
        ("NotAfter", FILETIME),
        ("Subject", CRYPT_DATA_BLOB),
        ("SubjectPublicKeyInfo", CERT_PUBLIC_KEY_INFO),
        ("IssuerUniqueId", CRYPT_BIT_BLOB),
        ("SubjectUniqueId", CRYPT_BIT_BLOB),
        ("cExtension", wt.DWORD),
        ("rgExtension", ctypes.c_void_p),
    ]


class CERT_CONTEXT(ctypes.Structure):
    _fields_ = [
        ("dwCertEncodingType", wt.DWORD),
        ("pbCertEncoded", ctypes.POINTER(ctypes.c_byte)),
        ("cbCertEncoded", wt.DWORD),
        ("pCertInfo", ctypes.POINTER(CERT_INFO)),
        ("hCertStore", ctypes.c_void_p),
    ]


# ---------------------------------------------------------------------------
# Win32-API-Funktionen laden
# ---------------------------------------------------------------------------
_crypt32 = ctypes.windll.crypt32  # type: ignore[attr-defined]

CertOpenStore = _crypt32.CertOpenStore
CertOpenStore.argtypes = [
    ctypes.c_char_p,  # lpszStoreProvider
    wt.DWORD,  # dwEncodingType
    ctypes.c_void_p,  # hCryptProv
    wt.DWORD,  # dwFlags
    ctypes.c_wchar_p,  # pvPara
]
CertOpenStore.restype = ctypes.c_void_p

CertFindCertificateInStore = _crypt32.CertFindCertificateInStore
CertFindCertificateInStore.argtypes = [
    ctypes.c_void_p,  # hCertStore
    wt.DWORD,  # dwCertEncodingType
    wt.DWORD,  # dwFindFlags
    wt.DWORD,  # dwFindType
    ctypes.c_void_p,  # pvFindPara
    ctypes.POINTER(CERT_CONTEXT),  # pPrevCertContext
]
CertFindCertificateInStore.restype = ctypes.POINTER(CERT_CONTEXT)

CertGetNameStringW = _crypt32.CertGetNameStringW
CertGetNameStringW.argtypes = [
    ctypes.POINTER(CERT_CONTEXT),  # pCertContext
    wt.DWORD,  # dwType
    wt.DWORD,  # dwFlags
    ctypes.c_void_p,  # pvTypePara
    ctypes.c_wchar_p,  # pszNameString
    wt.DWORD,  # cchNameString
]
CertGetNameStringW.restype = wt.DWORD

CertCloseStore = _crypt32.CertCloseStore
CertCloseStore.argtypes = [ctypes.c_void_p, wt.DWORD]
CertCloseStore.restype = wt.BOOL

CertFreeCertificateContext = _crypt32.CertFreeCertificateContext
CertFreeCertificateContext.argtypes = [ctypes.POINTER(CERT_CONTEXT)]
CertFreeCertificateContext.restype = wt.BOOL

_advapi32 = ctypes.windll.advapi32  # type: ignore[attr-defined]
CryptReleaseContext = _advapi32.CryptReleaseContext
CryptReleaseContext.argtypes = [ctypes.c_void_p, wt.DWORD]
CryptReleaseContext.restype = wt.BOOL

try:
    _ncrypt = ctypes.windll.ncrypt  # type: ignore[attr-defined]
    NCryptFreeObject = _ncrypt.NCryptFreeObject
    NCryptFreeObject.argtypes = [ctypes.c_void_p]
    NCryptFreeObject.restype = wt.DWORD
except Exception:
    NCryptFreeObject = None

# CryptAcquireCertificatePrivateKey – prüft ob Private Key vorhanden
CryptAcquireCertificatePrivateKey = _crypt32.CryptAcquireCertificatePrivateKey
CryptAcquireCertificatePrivateKey.argtypes = [
    ctypes.POINTER(CERT_CONTEXT),  # pCert
    wt.DWORD,  # dwFlags
    ctypes.c_void_p,  # pvParameters
    ctypes.POINTER(ctypes.c_void_p),  # phCryptProvOrNCryptKey
    ctypes.POINTER(wt.DWORD),  # pdwKeySpec
    ctypes.POINTER(wt.BOOL),  # pfCallerFreeProvOrNCryptKey
]
CryptAcquireCertificatePrivateKey.restype = wt.BOOL

CRYPT_ACQUIRE_SILENT_FLAG = 0x00000040
CRYPT_ACQUIRE_CACHE_FLAG = 0x00000001
CERT_NCRYPT_KEY_SPEC = 0xFFFFFFFF


# ---------------------------------------------------------------------------
# Hilfsfunktionen
# ---------------------------------------------------------------------------
def _filetime_to_datetime(ft: FILETIME) -> datetime:
    """Konvertiert Win32-FILETIME in Python-datetime (UTC)."""
    # FILETIME = 100-Nanosekunden-Intervalle seit 01.01.1601
    timestamp = (ft.dwHighDateTime << 32) + ft.dwLowDateTime
    # Differenz zwischen 1601 und 1970 in 100ns-Einheiten
    EPOCH_DIFF = 116444736000000000
    if timestamp <= EPOCH_DIFF:
        return datetime(1970, 1, 1, tzinfo=timezone.utc)
    unix_ts = (timestamp - EPOCH_DIFF) / 10_000_000
    return datetime.fromtimestamp(unix_ts, tz=timezone.utc)


def _get_cert_name(ctx: ctypes.POINTER(CERT_CONTEXT), issuer: bool = False) -> str:
    """Liest Subject- oder Issuer-Namen aus einem Zertifikatskontext."""
    buf = ctypes.create_unicode_buffer(256)
    flags = CERT_NAME_ISSUER_FLAG if issuer else 0
    CertGetNameStringW(ctx, CERT_NAME_SIMPLE_DISPLAY_TYPE, flags, None, buf, 256)
    return buf.value


def _get_thumbprint(ctx: ctypes.POINTER(CERT_CONTEXT)) -> str:
    """Berechnet den SHA-1-Thumbprint des Zertifikats."""
    import hashlib

    cert_data = ctypes.string_at(
        ctx.contents.pbCertEncoded,
        ctx.contents.cbCertEncoded,
    )
    return hashlib.sha1(cert_data).hexdigest().upper()


def _has_private_key(ctx: ctypes.POINTER(CERT_CONTEXT)) -> bool:
    """Prüft, ob das Zertifikat einen privaten Schlüssel besitzt."""
    hProv = ctypes.c_void_p()
    dwKeySpec = wt.DWORD()
    fCallerFree = wt.BOOL()
    result = CryptAcquireCertificatePrivateKey(
        ctx,
        CRYPT_ACQUIRE_SILENT_FLAG | CRYPT_ACQUIRE_CACHE_FLAG,
        None,
        ctypes.byref(hProv),
        ctypes.byref(dwKeySpec),
        ctypes.byref(fCallerFree),
    )
    if not result:
        return False

    # FIX #2: Akquirierte Key-Handles freigeben, um Handle-Leaks zu vermeiden.
    if bool(fCallerFree) and hProv.value:
        try:
            if dwKeySpec.value == CERT_NCRYPT_KEY_SPEC and NCryptFreeObject:
                NCryptFreeObject(hProv)
            else:
                CryptReleaseContext(hProv, 0)
        except Exception:
            pass

    return True


# ---------------------------------------------------------------------------
# Öffentliche API
# ---------------------------------------------------------------------------
def get_certificates_native(store_location: str = "CurrentUser") -> List[CertInfo]:
    """
    Liest Zertifikate aus dem Windows-Zertifikatsspeicher über Win32-API.

    Args:
        store_location: 'CurrentUser' oder 'LocalMachine'

    Returns:
        Liste von CertInfo-Objekten (nur gültige Zertifikate mit Private Key)
    """
    flags = (
        CERT_SYSTEM_STORE_CURRENT_USER
        if store_location == "CurrentUser"
        else CERT_SYSTEM_STORE_LOCAL_MACHINE
    )

    store = CertOpenStore(
        ctypes.c_char_p(CERT_STORE_PROV_SYSTEM),
        0,
        None,
        flags,
        "My",
    )
    if not store:
        raise OSError(
            f"Zertifikatsspeicher konnte nicht geöffnet werden "
            f"(Store: {store_location}\\My)"
        )

    certs: List[CertInfo] = []
    ctx = None
    now = datetime.now(timezone.utc)

    try:
        while True:
            ctx = CertFindCertificateInStore(
                store, ENCODING, 0, CERT_FIND_ANY, None, ctx
            )
            if not ctx:
                break

            not_after = _filetime_to_datetime(ctx.contents.pCertInfo.contents.NotAfter)

            # Nur gültige Zertifikate mit privatem Schlüssel
            if not_after <= now:
                continue
            if not _has_private_key(ctx):
                continue

            cert = CertInfo(
                subject=_get_cert_name(ctx, issuer=False),
                issuer=_get_cert_name(ctx, issuer=True),
                thumbprint=_get_thumbprint(ctx),
                not_after=not_after,
                has_private_key=True,
            )
            certs.append(cert)
    finally:
        CertCloseStore(store, 0)

    return certs


def get_certificates_powershell(store_location: str = "CurrentUser") -> List[CertInfo]:
    """
    Fallback: Liest Zertifikate über PowerShell.

    Args:
        store_location: 'CurrentUser' oder 'LocalMachine'

    Returns:
        Liste von CertInfo-Objekten
    """
    ps_script = f"""
    $certs = Get-ChildItem -Path "Cert:\\{store_location}\\My" |
        Where-Object {{ $_.HasPrivateKey -eq $true -and $_.NotAfter -gt (Get-Date) }} |
        Select-Object Subject, Issuer, Thumbprint,
            @{{Name='NotAfter'; Expression={{$_.NotAfter.ToString('o')}}}}
    $certs | ConvertTo-Json -Compress
    """

    result = subprocess.run(
        ["powershell", "-NoProfile", "-Command", ps_script],
        capture_output=True,
        text=True,
        timeout=30,
    )

    if result.returncode != 0:
        raise OSError(
            f"PowerShell-Fehler beim Lesen der Zertifikate: {result.stderr.strip()}"
        )

    output = result.stdout.strip()
    if not output or output == "null":
        return []

    data = json.loads(output)
    # PowerShell gibt bei einem einzelnen Ergebnis kein Array zurück
    if isinstance(data, dict):
        data = [data]

    certs: List[CertInfo] = []
    for item in data:
        not_after = datetime.fromisoformat(item["NotAfter"])
        if not_after.tzinfo is None:
            not_after = not_after.replace(tzinfo=timezone.utc)
        certs.append(
            CertInfo(
                subject=item.get("Subject", ""),
                issuer=item.get("Issuer", ""),
                thumbprint=item.get("Thumbprint", ""),
                not_after=not_after,
                has_private_key=True,
            )
        )

    return certs


def get_certificates(store_location: str = "CurrentUser") -> List[CertInfo]:
    """
    Liest Zertifikate – versucht zuerst die native Win32-API,
    fällt bei Fehler auf PowerShell zurück.

    Args:
        store_location: 'CurrentUser' oder 'LocalMachine'

    Returns:
        Liste von CertInfo-Objekten
    """
    try:
        return get_certificates_native(store_location)
    except Exception:
        return get_certificates_powershell(store_location)
