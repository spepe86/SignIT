<p align="center">
  <img src="assets/icon.ico" alt="SignIT Logo" width="96" />
</p>

<h1 align="center">Let's Do. | SignIT</h1>

<p align="center">
  <strong>Modernes Windows-Tool zum Signieren von EXE-, DLL- &amp; MSI-Dateien mit Code-Signing-Zertifikaten</strong>
</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#screenshots">Screenshots</a> •
  <a href="#installation">Installation</a> •
  <a href="#verwendung">Verwendung</a> •
  <a href="#selbst-bauen">Build</a> •
  <a href="#projektstruktur">Struktur</a> •
  <a href="#mitwirken">Mitwirken</a> •
  <a href="#lizenz">Lizenz</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Plattform-Windows%2010%2F11-0078D4?style=flat-square&logo=windows" alt="Windows" />
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python 3.10+" />
  <img src="https://img.shields.io/badge/GUI-CustomTkinter-1f6feb?style=flat-square" alt="CustomTkinter" />
  <img src="https://img.shields.io/badge/Lizenz-Apache%202.0-brightgreen?style=flat-square" alt="Apache 2.0" />
  <img src="https://img.shields.io/github/v/release/spepe86/SignIT?style=flat-square&label=Release" alt="Release" />
</p>

<p align="center">
  🇬🇧 <a href="README.md">English Version</a>
</p>

---

## Das Problem

Code-Signing mit `signtool.exe` bedeutet: kryptische Kommandozeilen-Flags zusammenbauen, den richtigen SDK-Pfad suchen, Zertifikats-Thumbprints manuell kopieren — und das Ganze für jede einzelne Datei wiederholen.

## Die Lösung

**SignIT** verpackt den gesamten Workflow in eine moderne, übersichtliche GUI:

> **SignTool finden** → **Zertifikat wählen** → **Dateien auswählen** → **Timestamp konfigurieren** → **Signieren**
>
> Fünf Klicks. Fertig.

---

## Features

### 🔐 Zertifikatsverwaltung
- Automatisches Laden aller gültigen Code-Signing-Zertifikate aus dem **Windows-Zertifikatsspeicher**
- Unterstützung für `CurrentUser` und `LocalMachine` Speicherorte
- Filtert nach Zertifikaten mit privatem Schlüssel, die noch gültig sind
- Nativer **Win32 Crypto API**-Zugriff via `ctypes` — PowerShell-Fallback inklusive

### 📁 Dateiauswahl
- Mehrfachauswahl über den nativen Windows-Datei-Dialog
- Unterstützt `.exe`, `.dll`, `.msi`, `.sys`, `.ocx`, `.cab`
- Einzelne Dateien vor dem Signieren entfernbar
- Zeigt Dateiname, Pfad und Größe auf einen Blick

### 🔧 SignTool-Integration
- **Automatische Erkennung** von `signtool.exe` im PATH und in Windows-SDK-Installationen (8.0 / 8.1 / 10.x)
- Bevorzugt automatisch die x64-Version
- Manueller Pfad jederzeit konfigurierbar

### 🕐 Timestamp-Server
- Voreingestellt auf **DigiCert** (Industriestandard)
- Dropdown mit gängigen Alternativen: Sectigo, GlobalSign, Comodo, SSL.com, Entrust
- Eigene URL jederzeit eingebbar

### ✍️ Signiervorgang
- Signiert mit **SHA-256** (`/fd sha256 /td sha256`)
- RFC 3161 Timestamping (`/tr`)
- Sequentielle Batch-Verarbeitung mehrerer Dateien
- **Echtzeit-Fortschrittsbalken** pro Datei
- **Farbcodiertes Live-Log**: 🟢 Erfolg · 🔴 Fehler · 🟡 Warnung · 🔵 Info

### 🎨 Benutzeroberfläche
- **Dark Theme** als Standard (Light Theme per Klick umschaltbar)
- Modernes Flat-Design mit CustomTkinter
- Zwei-Spalten-Layout: Konfiguration links, Live-Log rechts
- Statusleiste mit aktueller Aktion
- Log exportierbar als `.txt`
- Responsive — Mindestgröße 920 × 700 px

---

## Screenshots

> 📸 **Demnächst** — Screenshots werden mit dem nächsten Release ergänzt.

---

## Installation

### Option 1: Fertige EXE herunterladen *(empfohlen)*

1. Gehe zu [**Releases**](https://github.com/spepe86/SignIT/releases)
2. Lade die neueste `SignIT.exe` herunter
3. Starten — keine Installation nötig

> **Hinweis:** Windows SmartScreen kann beim ersten Start eine Warnung anzeigen. Klicke auf *„Weitere Informationen"* → *„Trotzdem ausführen"*. Das passiert, weil die EXE noch nicht mit einem EV-Zertifikat signiert ist.

### Option 2: Aus dem Quellcode starten

**Voraussetzungen:** Python 3.10+, Windows 10/11, optional ein Windows SDK

```bash
git clone https://github.com/spepe86/SignIT.git
cd SignIT

pip install -r requirements.txt

python main.py
```

---

## Verwendung

### 1. Zertifikat auswählen
- Speicherort wählen (`CurrentUser` oder `LocalMachine`)
- Klicke **„Aktualisieren"** um die Zertifikate zu laden
- Klicke auf das gewünschte Zertifikat in der Liste

### 2. Dateien hinzufügen
- Klicke **„Dateien hinzufügen…"**
- Wähle eine oder mehrere Dateien aus
- Einzelne Dateien über den **✕**-Button entfernen

### 3. SignTool konfigurieren
- SignIT sucht automatisch nach `signtool.exe`
- Falls nicht gefunden: Klicke **„Durchsuchen…"** um den Pfad manuell zu setzen
- Der Timestamp-Server ist auf DigiCert voreingestellt — bei Bedarf ändern

### 4. Signieren
- Zusammenfassung prüfen (Zertifikat + Dateianzahl)
- Klicke **„Jetzt signieren"**
- Dialog bestätigen
- Fortschritt im Live-Log verfolgen

**Ausgeführter Befehl pro Datei:**

```
signtool.exe sign /sha1 <THUMBPRINT> /tr <TIMESTAMP-URL> /td sha256 /fd sha256 <DATEI>
```

---

## Selbst bauen

```bash
pip install -r requirements.txt

# Empfohlen: mitgelieferte Spec-Datei verwenden
pyinstaller build.spec --clean --noconfirm

# Oder manuell
pyinstaller --onefile --windowed --name "SignIT" --icon=assets/icon.ico main.py
```

Ergebnis: `dist/SignIT.exe`

> **Tipp:** PyInstaller-EXEs werden gelegentlich von Antivirus-Software als verdächtig markiert. Das ist ein bekanntes PyInstaller-Problem, kein Sicherheitsrisiko. Signiere die fertige SignIT.exe mit deinem eigenen Zertifikat, um das zu lösen.

---

## Projektstruktur

```
SignIT/
├── main.py                 # Einstiegspunkt
├── gui/
│   ├── app.py              # Hauptfenster & Layout
│   ├── cert_panel.py       # Zertifikats-Auswahl-Panel
│   ├── file_panel.py       # Datei-Auswahl-Panel
│   ├── sign_panel.py       # SignTool-Konfiguration & Signierung
│   └── log_panel.py        # Farbcodiertes Live-Log mit Export
├── core/
│   ├── certstore.py        # Windows Certificate Store (Win32 API + PowerShell-Fallback)
│   ├── signer.py           # signtool.exe Wrapper (Subprocess + Threading)
│   └── utils.py            # Hilfsfunktionen (Pfadsuche, Timestamp-Server)
├── assets/
│   └── icon.ico            # App-Icon
├── requirements.txt
├── build.spec              # PyInstaller Build-Konfiguration
├── setup.iss               # Inno Setup Installer-Skript
└── LICENSE                 # Apache License 2.0
```

### Architektur

```
┌──────────────────────────────────────────────────┐
│               main.py (Einstiegspunkt)           │
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
│       (Win32 API)  (Subprocess) (Pfadsuche)     │
└──────────────────────────────────────────────────┘
```

---

## Technische Details

| Komponente | Details |
|---|---|
| **Zertifikatszugriff** | Native Win32 Crypto API via `ctypes` (`CertOpenStore`, `CertFindCertificateInStore`, `CryptAcquireCertificatePrivateKey`, `CertGetNameStringW`). PowerShell-Fallback via `Get-ChildItem Cert:\`. |
| **Signierung** | Läuft in einem Hintergrund-Thread. `subprocess.Popen` mit Echtzeit-stdout/stderr-Streaming. `CREATE_NO_WINDOW` verhindert Konsolen-Aufblitzen. |
| **GUI** | CustomTkinter 5.x mit responsivem `grid`/`pack` Layout. |

---

## Voraussetzungen

| Komponente | Version | Hinweis |
|---|---|---|
| **Windows** | 10 / 11 | Ältere Versionen evtl. kompatibel |
| **Python** | 3.10+ | Nur für Entwicklung / Selbst-Build |
| **signtool.exe** | Windows SDK | Wird automatisch erkannt |
| **Code-Signing-Zertifikat** | x509 | Im Windows-Zertifikatsspeicher installiert |

---

## FAQ

**F: Brauche ich ein Code-Signing-Zertifikat?**
A: Ja. SignIT hilft beim *Anwenden* des Zertifikats. Das Zertifikat selbst musst du von einer CA (DigiCert, Sectigo, GlobalSign etc.) erwerben und im Windows-Zertifikatsspeicher installieren.

**F: Funktioniert es mit EV-Zertifikaten (Extended Validation)?**
A: EV-Zertifikate auf einem Hardware-Token (z. B. SafeNet) erfordern möglicherweise eine PIN-Eingabe. SignIT leitet den signtool-Prozess korrekt weiter, aber der Token-Treiber öffnet seinen eigenen PIN-Dialog.

**F: Kann ich SignIT kommerziell nutzen?**
A: Ja. Die Apache 2.0 Lizenz erlaubt kommerzielle Nutzung, Modifikation und Weiterverbreitung. Einzige Bedingung: Namensnennung beibehalten (Copyright-Hinweis und LICENSE-Datei).

---

## Mitwirken

Beiträge sind willkommen! So kannst du helfen:

1. 🐛 **Bug melden** — öffne ein [Issue](https://github.com/spepe86/SignIT/issues)
2. 💡 **Feature vorschlagen** — öffne ein [Issue](https://github.com/spepe86/SignIT/issues) mit dem Label `enhancement`
3. 🔧 **Code beitragen** — forke das Repo und erstelle einen Pull Request

```bash
git clone https://github.com/spepe86/SignIT.git
cd SignIT
pip install -r requirements.txt
python main.py
```

---

## Lizenz

Dieses Projekt steht unter der **Apache License 2.0**.

Du darfst die Software frei nutzen, modifizieren und verbreiten — auch kommerziell. Einzige Pflicht: Copyright-Hinweis und LICENSE-Datei beibehalten.

Siehe [LICENSE](LICENSE) für den vollständigen Lizenztext.

---

<p align="center">
  <strong>Let's Do. | SignIT</strong> — Code-Signing, einfach gemacht.<br/>
  <sub>⭐ Gib dem Repo einen Stern, wenn es dir hilft!</sub>
</p>
