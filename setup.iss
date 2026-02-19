[Setup]
AppName=Let's Do. | SignIT
AppVersion=4.2
AppPublisher=Let's Do. - Inh. Peter Seidl
DefaultDirName={pf}\SignIT
DefaultGroupName=SignIT
OutputDir=installer_output
OutputBaseFilename=Setup_SignIT_V4.2
SetupIconFile=assets\icon.ico
UninstallDisplayIcon={app}\SignIT_V4.2.exe
Compression=lzma2/ultra64
SolidCompression=yes
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64compatible

[Files]
Source: "dist\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "assets\icon.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\SignIT"; Filename: "{app}\SignIT_V4.2.exe"; IconFilename: "{app}\icon.ico"
Name: "{commondesktop}\SignIT"; Filename: "{app}\SignIT_V4.2.exe"; IconFilename: "{app}\icon.ico"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Desktop-Verknüpfung erstellen"; GroupDescription: "Zusätzliche Optionen:"

[Run]
Filename: "{app}\SignIT_V4.2.exe"; Description: "Anwendung jetzt starten"; Flags: nowait postinstall skipifsilent runascurrentuser

[UninstallDelete]
Type: filesandordirs; Name: "{app}\logs"
Type: filesandordirs; Name: "{app}\config"
Type: filesandordirs; Name: "{app}\cache"
