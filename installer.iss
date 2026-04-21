[Setup]
AppName=Encrypter
AppVersion=1.0.0
DefaultDirName={autopf}\Encrypter
DefaultGroupName=Encrypter
UninstallDisplayIcon={app}\Encrypter.exe
Compression=lzma2
SolidCompression=yes
OutputDir=.
OutputBaseFilename=Encrypter-Setup
; Add your license file here if you want it to show during setup
 LicenseFile=LICENCE.txt

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\Encrypter.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Encrypter"; Filename: "{app}\Encrypter.exe"
Name: "{autodesktop}\Encrypter"; Filename: "{app}\Encrypter.exe"; Tasks: desktopicon

[Registry]
; Create the .enc extension association
Root: HKA; Subkey: "Software\Classes\.enc"; ValueType: string; ValueName: ""; ValueData: "EncrypterFile"; Flags: uninsdeletevalue
Root: HKA; Subkey: "Software\Classes\EncrypterFile"; ValueType: string; ValueName: ""; ValueData: "Encrypted Data File"; Flags: uninsdeletekey
; Use the icon embedded in your exe for all .enc files
Root: HKA; Subkey: "Software\Classes\EncrypterFile\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\Encrypter.exe,0"
; Associate the "Open" command with your app
Root: HKA; Subkey: "Software\Classes\EncrypterFile\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\Encrypter.exe"" ""%1"""

[Run]
Filename: "{app}\Encrypter.exe"; Description: "{cm:LaunchProgram,Encrypter}"; Flags: nowait postinstall skipifsilent