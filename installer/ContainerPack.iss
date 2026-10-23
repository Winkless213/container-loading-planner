; 装柜工作台 installer (Inno Setup 7)
; 先构建 PyInstaller 单文件 exe，再运行：
;   ISCC.exe installer\ContainerPack.iss

#define AppName "装柜工作台"
#define AppNameEn "Container Loading Planner"
#define AppVersion "1.0.1"
#define AppPublisher "Winkless213"
#define AppURL "https://github.com/Winkless213/container-loading-planner"
#define AppExe "ContainerPack.exe"
#define AppSrc "..\dist"

[Setup]
AppId={{0BD3081F-6E4E-45C3-892A-7C600609576D}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} {#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}/issues
AppUpdatesURL={#AppURL}/releases
VersionInfoVersion=1.0.1.0
VersionInfoDescription={#AppNameEn} {#AppVersion} installer
VersionInfoProductName={#AppNameEn}
DefaultDirName={localappdata}\Programs\{#AppNameEn}
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0
OutputDir=..\work\release\installer
OutputBaseFilename=Container-Loading-Planner-Setup-{#AppVersion}
UninstallDisplayIcon={app}\{#AppExe}
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
CloseApplications=yes
RestartApplications=no
LicenseFile=..\LICENSE
AllowNoIcons=yes
SetupLogging=yes

[Languages]
Name: "chinesesimplified"; MessagesFile: "compiler:Languages\ChineseSimplified.isl"

[Tasks]
Name: "desktopicon"; Description: "创建桌面快捷方式"; GroupDescription: "附加图标:"; Flags: checkedonce

[Files]
Source: "{#AppSrc}\ContainerPack.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\LICENSE"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\THIRD_PARTY_NOTICES.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\CHANGELOG.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\docs\USAGE.md"; DestDir: "{app}\docs"; Flags: ignoreversion
Source: "..\docs\DEVELOPMENT.md"; DestDir: "{app}\docs"; Flags: ignoreversion

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExe}"; WorkingDir: "{app}"
Name: "{group}\操作手册"; Filename: "{app}\docs\USAGE.md"
Name: "{group}\卸载 {#AppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExe}"; WorkingDir: "{app}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExe}"; Description: "启动 {#AppName}"; Flags: nowait postinstall skipifsilent; Check: ShouldLaunchApp

[Code]
var
  SelfTestPassed: Boolean;

function ShouldLaunchApp: Boolean;
begin
  Result := SelfTestPassed;
end;

function RuntimeFilesPresent: Boolean;
begin
  Result := FileExists(ExpandConstant('{app}\{#AppExe}'));
end;

function InitializeSetup: Boolean;
begin
  Result := True;
  if not IsWin64 then
  begin
    MsgBox('装柜工作台需要 64 位 Windows 10 或更高版本。', mbError, MB_OK);
    Result := False;
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  ResultCode: Integer;
begin
  if CurStep <> ssPostInstall then
    Exit;

  if not RuntimeFilesPresent then
  begin
    MsgBox('安装文件不完整：{#AppExe} 缺失或大小异常。' + #13#10 +
           '请重新下载安装包。', mbError, MB_OK);
    Exit;
  end;

  if Exec(ExpandConstant('{app}\{#AppExe}'), '--self-test',
          ExpandConstant('{app}'), SW_HIDE, ewWaitUntilTerminated, ResultCode) and
     (ResultCode = 0) then
  begin
    SelfTestPassed := True;
  end
  else
  begin
    MsgBox('安装完成，但启动自检失败。' + #13#10 +
           '请查看 %TEMP%\ContainerPack-self-test.log，或到 GitHub Issues 反馈。',
           mbError, MB_OK);
  end;
end;
