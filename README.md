<p align="center">
  <img src="assets/icon.ico" alt="SignIT Logo" width="96" />
</p>

<h1 align="center">Let's Do. | SignIT</h1>

<p align="center">
  <strong>Modern Windows GUI for signing EXE, DLL &amp; MSI files with code-signing certificates</strong>
</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#screenshots">Screenshots</a> •
  <a href="#installation">Installation</a> •
  <a href="#usage">Usage</a> •
  <a href="#build-from-source">Build</a> •
  <a href="#project-structure">Structure</a> •
  <a href="#contributing">Contributing</a> •
  <a href="#license">License</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Platform-Windows%2010%2F11-0078D4?style=flat-square&logo=windows" alt="Windows" />
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python 3.10+" />
  <img src="https://img.shields.io/badge/GUI-CustomTkinter-1f6feb?style=flat-square" alt="CustomTkinter" />
  <img src="https://img.shields.io/badge/License-Apache%202.0-brightgreen?style=flat-square" alt="Apache 2.0" />
  <img src="https://img.shields.io/github/v/release/spepe86/SignIT?style=flat-square&label=Release" alt="Release" />
</p>

<p align="center">
  🇩🇪 <a href="README.de.md">Deutsche Version</a>
</p>

---

## The Problem

Signing executables with `signtool.exe` means juggling cryptic command-line flags, hunting for the right SDK path, copying certificate thumbprints by hand — and repeating all of that for every single file.

## The Solution

**SignIT** wraps the entire workflow in a clean, modern GUI:

> **Find SignTool** → **Pick Certificate** → **Select Files** → **Configure Timestamp** → **Sign**
>
> Five clicks. Done.

---

## Features

### 🔐 Certificate Management
- Automatically loads all valid code-signing certificates from the **Windows Certificate Store**
- Supports `CurrentUser` and `LocalMachine` store locations
- Filters for certificates with a private key that are still valid
- Native **Win32 Crypto API** access via `ctypes` — PowerShell fallback included

### 📁 File Selection
- Multi-select via native Windows file dialog
- Supports `.exe`, `.dll`, `.msi`, `.sys`, `.ocx`, `.cab`
- Remove individual files before signing
- Shows file name, path, and size at a glance

### 🔧 SignTool Integration
- **Auto-detection** of `signtool.exe` in PATH and Windows SDK installations (8.0 / 8.1 / 10.x)
- Prefers the x64 binary automatically
- Manual path override available at any time

### 🕐 Timestamp Server
- Pre-configured with **DigiCert** (industry standard)
- Dropdown with popular alternatives: Sectigo, GlobalSign, Comodo, SSL.com, Entrust
- Custom URL input supported

### ✍️ Signing Process
- Signs with **SHA-256** (`/fd sha256 /td sha256`)
- RFC 3161 timestamping (`/tr`)
- Sequential batch processing of multiple files
- **Real-time progress bar** per file
- **Color-coded live log**: 🟢 Success · 🔴 Error · 🟡 Warning · 🔵 Info

### 🎨 User Interface
- **Dark theme** by default (light theme toggle)
- Modern flat design powered by CustomTkinter
- Two-column layout: configuration on the left, live log on the right
- Status bar with current action
- Export log as `.txt`
- Responsive — minimum size 920 × 700 px

---

## Screenshots

> 📸 **Coming soon** — screenshots will be added with the next release.

---

## Installation

### Option 1: Download the ready-made EXE *(recommended)*

1. Head over to [**Releases**](https://github.com/spepe86/SignIT/releases)
2. Download the latest `SignIT.exe`
3. Run it — no installation required

> **Note:** Windows SmartScreen may show a warning on first launch. Click *"More info"* → *"Run anyway"*. This happens because the EXE is not yet signed with an EV certificate.

### Option 2: Run from source

**Requirements:** Python 3.10+, Windows 10/11, optionally a Windows SDK

```bash
git clone https://github.com/spepe86/SignIT.git
cd SignIT

pip install -r requirements.txt

python main.py
```

---

## Usage

### 1. Select a Certificate
- Choose the store location (`CurrentUser` or `LocalMachine`)
- Click **"Refresh"** to load certificates
- Click on the desired certificate in the list

### 2. Add Files
- Click **"Add files…"**
- Select one or more files
- Remove individual files with the **✕** button

### 3. Configure SignTool
- SignIT searches for `signtool.exe` automatically
- If not found, click **"Browse…"** to set the path manually
- The timestamp server defaults to DigiCert — change if needed

### 4. Sign
- Review the summary (certificate + file count)
- Click **"Sign now"**
- Confirm the dialog
- Watch progress in the live log

**Command executed per file:**

```
signtool.exe sign /sha1 <THUMBPRINT> /tr <TIMESTAMP-URL> /td sha256 /fd sha256 <FILE>
```

---

## Build from Source

```bash
pip install -r requirements.txt

# Recommended: use the included spec file
pyinstaller build.spec --clean --noconfirm

# Or build manually
pyinstaller --onefile --windowed --name "SignIT" --icon=assets/icon.ico main.py
```

Output: `dist/SignIT.exe`

> **Tip:** PyInstaller-built standalone EXEs are occasionally flagged by antivirus software. This is a known PyInstaller issue, not a security risk. Sign the resulting EXE with your own certificate to resolve this.

---

## Project Structure

```
SignIT/
├── main.py                 # Entry point
├── gui/
│   ├── app.py              # Main window & layout
│   ├── cert_panel.py       # Certificate selection panel
│   ├── file_panel.py       # File selection panel
│   ├── sign_panel.py       # SignTool config & signing
│   └── log_panel.py        # Color-coded live log with export
├── core/
│   ├── certstore.py        # Windows Certificate Store (Win32 API + PowerShell fallback)
│   ├── signer.py           # signtool.exe wrapper (subprocess + threading)
│   └── utils.py            # Helpers (path search, timestamp servers)
├── assets/
│   └── icon.ico            # App icon
├── requirements.txt
├── build.spec              # PyInstaller build config
├── setup.iss               # Inno Setup installer script
└── LICENSE                 # Apache License 2.0
```

### Architecture

```
┌──────────────────────────────────────────────────┐
│                 main.py (Entry Point)            │
│                        │                         │
│                  gui/app.py (SignITApp)           │
│            ┌─────┼─────┬──────────┐              │
│            │     │     │          │               │
│       cert_panel file_panel sign_panel log_panel  │
│            │     │     │          │               │
│            └─────┴─────┴──────────┘               │
│                        │                         │
│            ┌───────────┼───────────┐             │
│            │           │           │             │
│       certstore.py  signer.py   utils.py        │
│       (Win32 API)  (subprocess) (path search)   │
└──────────────────────────────────────────────────┘
```

---

## Technical Details

| Component | Details |
|---|---|
| **Certificate access** | Native Win32 Crypto API via `ctypes` (`CertOpenStore`, `CertFindCertificateInStore`, `CryptAcquireCertificatePrivateKey`, `CertGetNameStringW`). PowerShell fallback via `Get-ChildItem Cert:\`. |
| **Signing** | Runs in a background thread. `subprocess.Popen` with real-time stdout/stderr streaming. `CREATE_NO_WINDOW` flag prevents console flash. |
| **GUI** | CustomTkinter 5.x with responsive `grid`/`pack` layout. |

---

## Requirements

| Component | Version | Note |
|---|---|---|
| **Windows** | 10 / 11 | Older versions may work |
| **Python** | 3.10+ | Only for development / self-build |
| **signtool.exe** | Windows SDK | Auto-detected |
| **Code-Signing Certificate** | x509 | Installed in the Windows Certificate Store |

---

## FAQ

**Q: Do I need a code-signing certificate?**
A: Yes. SignIT helps you *apply* the certificate. You need to purchase the certificate itself from a CA (DigiCert, Sectigo, GlobalSign, etc.) and install it in the Windows Certificate Store.

**Q: Does it work with EV (Extended Validation) certificates?**
A: EV certificates stored on a hardware token (e.g. SafeNet) may require a PIN prompt during signing. SignIT passes the signtool process through correctly, but the token driver will open its own PIN dialog.

**Q: Can I use SignIT commercially?**
A: Absolutely. The Apache 2.0 license allows commercial use, modification, and redistribution. Just keep the copyright notice and LICENSE file.

---

## Contributing

Contributions are welcome! Here's how you can help:

1. 🐛 **Report a bug** — open an [Issue](https://github.com/spepe86/SignIT/issues)
2. 💡 **Suggest a feature** — open an [Issue](https://github.com/spepe86/SignIT/issues) with the `enhancement` label
3. 🔧 **Contribute code** — fork the repo and open a Pull Request

```bash
git clone https://github.com/spepe86/SignIT.git
cd SignIT
pip install -r requirements.txt
python main.py
```

---

## License

This project is licensed under the **Apache License 2.0**.

You are free to use, modify, and distribute this software — including for commercial purposes. The only requirement is to retain the copyright notice and LICENSE file.

See [LICENSE](LICENSE) for the full text.

---

<p align="center">
  <strong>Let's Do. | SignIT</strong> — Code signing, made simple.<br/>
  <sub>⭐ Star this repo if it helps you!</sub>
</p>
