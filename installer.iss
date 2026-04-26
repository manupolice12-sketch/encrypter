[Setup]
AppName=Encrypter
AppVersion=1.3.0
DefaultDirName={autopf}\Encrypter
DefaultGroupName=Encrypter
UninstallDisplayIcon={app}\Encrypter.exe
Compression=lzma2
SolidCompression=yes
OutputDir=.
OutputBaseFilename=Encrypter-Setup
LicenseFile=LICENCE.txt
PrivilegesRequired=admin
ChangesAssociations=yes

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\Encrypter.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Encrypter"; Filename: "{app}\Encrypter.exe"
Name: "{autodesktop}\Encrypter"; Filename: "{app}\Encrypter.exe"; Tasks: desktopicon

[Registry]
Root: HKA; Subkey: "Software\Classes\.enc"; ValueType: string; ValueName: ""; ValueData: "EncrypterFile"; Flags: uninsdeletevalue
Root: HKA; Subkey: "Software\Classes\EncrypterFile"; ValueType: string; ValueName: ""; ValueData: "Encrypted Data File"; Flags: uninsdeletekey
Root: HKA; Subkey: "Software\Classes\EncrypterFile\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\Encrypter.exe,0"
Root: HKA; Subkey: "Software\Classes\EncrypterFile\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\Encrypter.exe"" ""%1"""

[Run]
Filename: "{app}\Encrypter.exe"; Description: "{cm:LaunchProgram,Encrypter}"; Flags: nowait postinstall skipifsilent