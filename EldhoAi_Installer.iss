#define MyAppName "EldhoAi"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "REAL_ELDHO"
#define MyAppExeName "EldhoAi.exe"

[Setup]
AppId={{3544A14B-1FB2-419A-8616-8DF72D536DEF}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={localappdata}\EldhoAi
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
OutputDir=dist
OutputBaseFilename=EldhoAi_Setup_1.0.0
SetupIconFile=EldhoAi.ico
UninstallDisplayIcon={app}\EldhoAi.exe
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
CloseApplications=yes
RestartApplications=no

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional shortcuts:"; Flags: unchecked

[Dirs]
; The application stores user data in a writable per-user location.
; These folders are deliberately not populated with personal data by Setup.
Name: "{app}\data"
Name: "{app}\logs"

[Files]
; Copy the entire PyInstaller one-folder build, but do not package private chats,
; image attachments, per-user API secrets, logs, or temporary files in the installer.
Source: "dist\EldhoAi\*"; DestDir: "{app}"; Excludes: "\data\*,.env,\logs\*,*.log,*.tmp,*.bak"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\EldhoAi"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; IconFilename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\EldhoAi"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; IconFilename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch EldhoAi"; WorkingDir: "{app}"; Flags: nowait postinstall skipifsilent
