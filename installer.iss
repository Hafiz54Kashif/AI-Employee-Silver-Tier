[Setup]
AppName=AI Employee
AppVersion=1.0
AppPublisher=AI Employee Pro
DefaultDirName={localappdata}\AI Employee
DefaultGroupName=AI Employee
OutputDir=D:\Agentic AI\Assignments\AI_Employee_Project\AI_Employee_Project\installer_output
OutputBaseFilename=AI_Employee_Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
SetupIconFile=
UninstallDisplayIcon={app}\AI_Employee.exe

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create Desktop Shortcut"; GroupDescription: "Additional Icons:"
Name: "startup"; Description: "Start AI Employee when Windows starts"; GroupDescription: "Startup:"

[Files]
Source: "D:\Agentic AI\Assignments\AI_Employee_Project\AI_Employee_Project\dist\AI_Employee\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\AI Employee"; Filename: "{app}\AI_Employee.exe"
Name: "{group}\Uninstall AI Employee"; Filename: "{uninstallexe}"
Name: "{commondesktop}\AI Employee"; Filename: "{app}\AI_Employee.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\AI_Employee.exe"; Description: "Launch AI Employee"; Flags: nowait postinstall skipifsilent

[Registry]
Root: HKCU; Subkey: "SOFTWARE\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "AI Employee"; ValueData: """{app}\AI_Employee.exe"""; Flags: uninsdeletevalue; Tasks: startup
