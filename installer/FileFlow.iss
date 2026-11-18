; Inno Setup Script for FileFlow
; Compiles FileFlow into a single setup.exe installer with complete uninstallation support

#define MyAppName "FileFlow"
#define MyAppVersion "1.0.3"
#define MyAppPublisher "FileFlow Open Source"
#define MyAppURL "https://github.com/nigam-30/fileflow"
#define MyAppExeName "FileFlow.exe"

[Setup]
AppId={{9F5712E4-05A9-4B52-87C3-899131C3C620}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={userpf}\{#MyAppName}
DisableProgramGroupPage=no
DefaultGroupName={#MyAppName}
OutputDir=..\dist
OutputBaseFilename=FileFlow-Setup-v{#MyAppVersion}
SetupIconFile=..\icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallDisplayName={#MyAppName}
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
CloseApplications=yes
CloseApplicationsFilter=FileFlow.exe

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "startwithwindows"; Description: "Start FileFlow when Windows boots"; GroupDescription: "Startup:"

[Files]
; Source files built by PyInstaller
Source: "..\dist\FileFlow\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Registry]
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "FileFlow"; ValueData: """{app}\{#MyAppExeName}"" --minimized"; Flags: uninsdeletevalue; Tasks: startwithwindows

[UninstallDelete]
Type: filesandordirs; Name: "{app}"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
// Close FileFlow if running before uninstall starts
function InitializeUninstall(): Boolean;
var
  ErrorCode: Integer;
begin
  Result := True;
  // Gracefully attempt to terminate FileFlow if currently active
  Exec('taskkill.exe', '/F /IM FileFlow.exe', '', SW_HIDE, ewWaitUntilTerminated, ErrorCode);
end;

// Ask user if they also wish to delete their saved rules & database
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  DataDir: String;
begin
  if CurUninstallStep = usPostUninstall then
  begin
    DataDir := ExpandConstant('{userappdata}\FileFlowData');
    if DirExists(DataDir) then
    begin
      if MsgBox('Would you like to delete your FileFlow rules and database?' + #13#10 + #13#10 +
                'Folder: ' + DataDir + #13#10#13#10 +
                'Click YES to remove all saved rules and logs.' + #13#10 +
                'Click NO to keep your rules for future installations.',
                mbConfirmation, MB_YESNO or MB_DEFBUTTON2) = IDYES then
      begin
        DelTree(DataDir, True, True, True);
      end;
    end;
  end;
end;

