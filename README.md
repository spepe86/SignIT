<p align="center">
  <img src="assets/icon.ico" alt="SignIT Logo" width="80" />
</p>

<h1 align="center">Let's Do. | SignIT</h1>

<p align="center">
  <strong>Modernes Windows-Tool zum Signieren von EXE-Dateien mit Code-Signing-Zertifikaten</strong>
</p>

<p align="center">
  <a href="#features">Features</a> &bull;
  <a href="#screenshots">Screenshots</a> &bull;
  <a href="#installation">Installation</a> &bull;
  <a href="#verwendung">Verwendung</a> &bull;
  <a href="#selbst-bauen">Selbst bauen</a> &bull;
  <a href="#projektstruktur">Projektstruktur</a> &bull;
  <a href="#lizenz">Lizenz</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Plattform-Windows-blue?style=flat-square&logo=windows" alt="Windows" />
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776ab?style=flat-square&logo=python&logoColor=white" alt="Python 3.10+" />
  <img src="https://img.shields.io/badge/GUI-CustomTkinter-1f6feb?style=flat-square" alt="CustomTkinter" />
  <img src="https://img.shields.io/badge/Lizenz-Apache%202.0-brightgreen?style=flat-square" alt="Apache 2.0" />
</p>

---

## Was ist SignIT?

**SignIT** ist eine moderne, benutzerfreundliche Desktop-Anwendung fuer Windows, die den gesamten Workflow zum Signieren von ausfuehrbaren Dateien (`.exe`, `.dll`, `.msi`, `.sys`, `.cab`) mit Code-Signing-Zertifikaten abbildet.

Anstatt kryptische Kommandozeilen-Befehle zusammenzubauen, fuehrt SignIT Sie Schritt fuer Schritt durch den Prozess -- mit einer uebersichtlichen grafischen Oberflaeche, Live-Feedback und klaren Fehlermeldungen.

### Das Problem

Code-Signing mit `signtool.exe` erfordert normalerweise:
- Den korrekten Pfad zu `signtool.exe` kennen
- Den SHA-1 Thumbprint des Zertifikats manuell heraussuchen
- Lange Kommandozeilen-Befehle korrekt zusammenbauen
- Bei mehreren Dateien: alles einzeln wiederholen

### Die Loesung

SignIT macht das mit **5 Klicks**:

> **SignTool finden** -> **Zertifikat waehlen** -> **Dateien waehlen** -> **Timestamp konfigurieren** -> **Signieren**

---

## Features

### Zertifikatsverwaltung
- Automatisches Laden aller gueltigen Code-Signing-Zertifikate aus dem Windows-Zertifikatsspeicher
- Unterstuetzung fuer `CurrentUser` und `LocalMachine` Speicherorte
- Filtert automatisch: nur Zertifikate mit privatem Schluessel, die noch gueltig sind
- Tabellarische Anzeige mit **Subject**, **Aussteller**, **Gueltig bis** und **Thumbprint**
- Nativer Win32-API-Zugriff via `ctypes` (kein Python-Wrapper noetig) mit PowerShell-Fallback

### Dateiauswahl
- Mehrfachauswahl ueber den nativen Windows-Datei-Dialog
- Unterstuetzung fuer `.exe`, `.dll`, `.msi`, `.sys`, `.ocx`, `.cab`
- Dateien einzeln wieder entfernbar
- Anzeige von Dateiname, Pfad und Dateigroesse

### SignTool-Integration
- **Automatische Suche** nach `signtool.exe` im System-PATH und in Windows SDK-Installationen
- Unterstuetzt Windows SDK 8.0, 8.1 und 10.x
- Bevorzugt automatisch die x64-Version
- Manueller Pfad jederzeit konfigurierbar

### Timestamp-Server
- Vorbelegt mit **DigiCert** (Industriestandard)
- Dropdown mit gaengigen Alternativen:
  - DigiCert, Sectigo, GlobalSign, Comodo, SSL.com, Entrust
- Eigene URL jederzeit eingebbar

### Signiervorgang
- Signiert mit SHA-256 (`/fd sha256 /td sha256`)
- RFC 3161 Timestamping (`/tr`)
- Sequentielle Verarbeitung mehrerer Dateien
- **Echtzeit-Fortschrittsbalken** pro Datei
- **Live-Log** mit farbiger Hervorhebung:
  - Gruen = Erfolg
  - Rot = Fehler
  - Gelb = Warnung
  - Blau = Info

### Benutzeroberflaeche
- **Dark Theme** als Standard (Light Theme per Klick umschaltbar)
- Modernes Flat-Design mit CustomTkinter
- Zwei-Spalten-Layout: Konfiguration links, Live-Log rechts
- Statusleiste mit aktueller Aktion
- Log exportierbar als `.txt`-Datei
- Mindestgroesse 920x700px, responsive

---

## Screenshots

> **Hinweis:** Screenshots koennen nach dem ersten Start der Anwendung hinzugefuegt werden.

<!--
![SignIT Hauptfenster](docs/screenshot-main.png)
![Signiervorgang](docs/screenshot-signing.png)
-->

---

## Installation

### Option 1: Fertige EXE herunterladen (empfohlen)

1. Gehen Sie zu [**Releases**](../../releases)
2. Laden Sie die neueste `SignIT.exe` herunter
3. Starten Sie die EXE -- keine Installation noetig

> **Hinweis:** Windows SmartScreen kann beim ersten Start eine Warnung anzeigen. Klicken Sie auf *"Weitere Informationen"* -> *"Trotzdem ausfuehren"*. Dies passiert, weil die EXE (noch) nicht mit einem EV-Zertifikat signiert ist.

### Option 2: Aus dem Quellcode starten

**Voraussetzungen:**
- Python 3.10 oder neuer
- Windows 10/11
- Optional: Windows SDK (fuer `signtool.exe`)

```bash
# Repository klonen
git clone https://github.com/IHR-USERNAME/signit.git
cd signit

# Abhaengigkeiten installieren
pip install -r requirements.txt

# Starten
python main.py
```

---

## Verwendung

### 1. Zertifikat auswaehlen

- Waehlen Sie den Speicherort (`CurrentUser` oder `LocalMachine`)
- Klicken Sie **"Aktualisieren"** um die Zertifikate zu laden
- Klicken Sie auf das gewuenschte Zertifikat in der Liste

### 2. Dateien hinzufuegen

- Klicken Sie **"Dateien hinzufuegen..."**
- Waehlen Sie eine oder mehrere Dateien aus
- Einzelne Dateien koennen ueber den **X**-Button wieder entfernt werden

### 3. SignTool konfigurieren

- SignIT sucht automatisch nach `signtool.exe`
- Falls nicht gefunden: Klicken Sie **"Durchsuchen..."** um den Pfad manuell anzugeben
- Der **Timestamp-Server** ist auf DigiCert voreingestellt -- bei Bedarf aendern

### 4. Signieren

- Pruefen Sie die Zusammenfassung (Zertifikat + Dateianzahl)
- Klicken Sie **"Jetzt signieren"**
- Bestaetigen Sie den Dialog
- Verfolgen Sie den Fortschritt im Live-Log rechts

### Ausgefuehrter Befehl

SignIT fuehrt pro Datei folgenden Befehl aus:

```
signtool.exe sign /sha1 <THUMBPRINT> /tr <TIMESTAMP-URL> /td sha256 /fd sha256 <DATEI>
```

---

## Selbst bauen

### Voraussetzungen

```bash
pip install -r requirements.txt
```

### Als EXE kompilieren

```bash
# Mit der mitgelieferten Spec-Datei (empfohlen)
pyinstaller build.spec --clean --noconfirm

# Oder manuell
pyinstaller --onefile --windowed --name "SignIT" --icon=assets/icon.ico main.py
```

Die fertige EXE liegt danach unter `dist/SignIT.exe`.

### Bekannte Build-Hinweise

- **CustomTkinter-Assets:** Die `build.spec` kopiert die CustomTkinter-Theme-Dateien automatisch mit. Bei manuellem Build ggf. `--hidden-import customtkinter` und `--add-data` ergaenzen.
- **Antivirus-Falschmeldungen:** Standalone-EXEs von PyInstaller werden gelegentlich von Antivirus-Software als verdaechtig markiert. Das ist ein bekanntes Problem von PyInstaller und kein Sicherheitsrisiko.

---

## Projektstruktur

```
signit/
├── main.py                 # Entry-Point
├── gui/
│   ├── __init__.py
│   ├── app.py              # Hauptfenster & Layout (SignITApp)
│   ├── cert_panel.py       # Zertifikats-Auswahl-Panel
│   ├── file_panel.py       # Datei-Auswahl-Panel
│   ├── sign_panel.py       # SignTool-Konfiguration & Signierung
│   └── log_panel.py        # Farbiges Live-Log mit Export
├── core/
│   ├── __init__.py
│   ├── certstore.py        # Windows Certificate Store (Win32 API + PowerShell-Fallback)
│   ├── signer.py           # signtool.exe Wrapper (Subprocess + Threading)
│   └── utils.py            # Hilfsfunktionen (Pfadsuche, Timestamp-Server)
├── assets/
│   └── icon.ico            # App-Icon
├── requirements.txt        # Python-Abhaengigkeiten
├── build.spec              # PyInstaller Build-Konfiguration
├── LICENSE                 # Apache License 2.0
├── .gitignore
└── README.md
```

### Architektur

```
┌─────────────────────────────────────────────────────────┐
│                    main.py (Entry-Point)                │
│                          │                              │
│                    gui/app.py (SignITApp)                │
│                ┌─────┼─────┬──────────┐                 │
│                │     │     │          │                  │
│           cert_panel file_panel sign_panel  log_panel    │
│                │     │     │          │                  │
│                └─────┴─────┴──────────┘                  │
│                          │                              │
│              ┌───────────┼───────────┐                  │
│              │           │           │                  │
│         certstore.py  signer.py   utils.py              │
│         (Win32 API)   (subprocess) (Pfadsuche)          │
└─────────────────────────────────────────────────────────┘
```

---

## Technische Details

### Zertifikatsspeicher-Zugriff

SignIT nutzt die **native Win32 Crypto API** ueber Python `ctypes`:

- `CertOpenStore` -- oeffnet den Zertifikatsspeicher
- `CertFindCertificateInStore` -- iteriert ueber alle Zertifikate
- `CryptAcquireCertificatePrivateKey` -- prueft ob ein privater Schluessel vorhanden ist
- `CertGetNameStringW` -- liest Subject/Issuer als lesbaren String

Falls die native API fehlschlaegt (z.B. wegen Berechtigungen), wechselt SignIT automatisch auf einen **PowerShell-Fallback** (`Get-ChildItem Cert:\`).

### Signiervorgang

- Laeuft in einem **Hintergrund-Thread**, damit die GUI nicht einfriert
- `subprocess.Popen` mit Echtzeit-stdout/stderr-Streaming
- Exit-Code-Auswertung: `0` = Erfolg, alles andere = Fehler
- `CREATE_NO_WINDOW` Flag verhindert Konsolenfenster-Aufblitzen

### GUI-Framework

- **CustomTkinter 5.x** -- modernes Tkinter-Derivat mit Dark/Light Theme
- Komplett responsives Layout mit `grid` und `pack` Managern
- Alle UI-Texte auf **Deutsch**

---

## Voraussetzungen

| Komponente | Version | Hinweis |
|---|---|---|
| **Windows** | 10 / 11 | Aeltere Versionen evtl. kompatibel |
| **Python** | 3.10+ | Nur fuer Entwicklung / Selbst-Build |
| **signtool.exe** | Windows SDK | Wird automatisch gesucht |
| **Code-Signing-Zertifikat** | x509 | Im Windows-Zertifikatsspeicher installiert |

---

## Abhaengigkeiten

| Paket | Zweck |
|---|---|
| [customtkinter](https://github.com/TomSchimansky/CustomTkinter) | Modernes GUI-Framework |
| [Pillow](https://python-pillow.org/) | Bild-Verarbeitung (fuer CustomTkinter) |
| [pyinstaller](https://pyinstaller.org/) | EXE-Kompilierung (nur Build) |

---

## Mitwirken

Beitraege sind willkommen! So koennen Sie helfen:

1. **Bug melden** -- oeffnen Sie ein [Issue](../../issues)
2. **Feature vorschlagen** -- oeffnen Sie ein [Issue](../../issues) mit dem Label `enhancement`
3. **Code beitragen** -- forken Sie das Repo und erstellen Sie einen Pull Request

### Entwicklungsumgebung einrichten

```bash
git clone https://github.com/IHR-USERNAME/signit.git
cd signit
pip install -r requirements.txt
python main.py
```

---

## FAQ

**Q: Brauche ich ein Code-Signing-Zertifikat?**
A: Ja. SignIT hilft beim _Anwenden_ des Zertifikats. Das Zertifikat selbst muessen Sie von einer Certificate Authority (CA) wie DigiCert, Sectigo, GlobalSign etc. erwerben und im Windows-Zertifikatsspeicher installieren.

**Q: Funktioniert SignIT auch mit EV-Zertifikaten (Extended Validation)?**
A: EV-Zertifikate, die auf einem Hardware-Token (z.B. SafeNet) gespeichert sind, erfordern moeglicherweise eine PIN-Eingabe waehrend des Signiervorgangs. SignIT leitet den signtool-Prozess korrekt weiter, aber der Token-Treiber oeffnet seinen eigenen PIN-Dialog.

**Q: Warum wird meine EXE von Antivirus-Software blockiert?**
A: PyInstaller-gebaute EXEs werden manchmal faelschlicherweise als verdaechtig markiert. Das ist ein branchenbekanntes Problem. Signieren Sie die fertige SignIT.exe selbst mit Ihrem Code-Signing-Zertifikat, um dieses Problem zu loesen.

**Q: Kann ich SignIT kommerziell nutzen?**
A: Ja. Die Apache 2.0 Lizenz erlaubt kommerzielle Nutzung, Modifikation und Weiterverbreitung. Einzige Bedingung: Namensnennung beibehalten (Copyright-Hinweis und LICENSE-Datei).

---

## Lizenz

Dieses Projekt steht unter der **Apache License 2.0**.

Das bedeutet, Sie duerfen:
- Den Code **kommerziell nutzen**
- Den Code **modifizieren**
- Den Code **weiterverbreiten**
- Abgeleitete Werke unter einer **anderen Lizenz** veroeffentlichen

Einzige Pflicht: **Namensnennung** -- behalten Sie den Copyright-Hinweis und die LICENSE-Datei bei.

Siehe [LICENSE](LICENSE) fuer den vollstaendigen Lizenztext.

---

<p align="center">
  <strong>Let's Do. | SignIT</strong> &mdash; Code-Signing, einfach gemacht.
</p>
