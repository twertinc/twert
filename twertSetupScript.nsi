; Script generated by the HM NIS Edit Script Wizard.

; HM NIS Edit Wizard helper defines
!define PRODUCT_NAME "Twert"
!define PRODUCT_VERSION "0.0.4"
!define PRODUCT_PUBLISHER "Twert, Inc."
!define PRODUCT_WEB_SITE "https://twert.net/"
!define PRODUCT_DIR_REGKEY "Software\Microsoft\Windows\CurrentVersion\App Paths\nssm.exe"
!define PRODUCT_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"
!define PRODUCT_UNINST_ROOT_KEY "HKLM"

; MUI 1.67 compatible ------
!include "MUI.nsh"

; MUI Settings
!define MUI_ABORTWARNING
!define MUI_ICON "favicon.ico"
!define MUI_UNICON "${NSISDIR}\Contrib\Graphics\Icons\modern-uninstall.ico"

; Welcome page
!insertmacro MUI_PAGE_WELCOME
; Directory page
!insertmacro MUI_PAGE_DIRECTORY
; Instfiles page
!insertmacro MUI_PAGE_INSTFILES


; Uninstaller pages
!insertmacro MUI_UNPAGE_INSTFILES

; Language files
!insertmacro MUI_LANGUAGE "English"

; MUI end ------

Name "${PRODUCT_NAME} ${PRODUCT_VERSION}"
OutFile "twertSetup.exe"
InstallDir "$PROGRAMFILES\Twert"
InstallDirRegKey HKLM "${PRODUCT_DIR_REGKEY}" ""
ShowInstDetails show
ShowUnInstDetails show

Section "MainSection" SEC01
  SetOutPath "$INSTDIR"
  SetOverwrite try
  File "twertexe\nblocker.sqlite3"
  File "twertexe\nssm.exe"
  CreateDirectory "$SMPROGRAMS\Twert"
  CreateShortCut "$SMPROGRAMS\Twert\Twert.lnk" "$INSTDIR\nssm.exe"
  CreateShortCut "$DESKTOP\Twert.lnk" "$INSTDIR\nssm.exe"
  SetOutPath "$INSTDIR\Prerequisites"
  File "twertexe\Prerequisites\npcap-1.71.exe"
  SetOutPath "$INSTDIR"
  File "twertexe\run.exe"
  File "twertexe\runStartService.bat"
  File "twertexe\runStopService.bat"
  File "twertexe\sniffer.exe"
  File "twertexe\snifferStartService.bat"
  File "twertexe\snifferStopService.bat"
  File "twertexe\tray.exe"
  File "twertexe\trayStopExe.bat"
  
  ExecWait '"$INSTDIR\Prerequisites\npcap-1.71.exe"'
  ExecWait '"$INSTDIR\snifferStartService.bat"'
  ExecWait '"$INSTDIR\runStartService.bat"'
  CreateShortCut "$SMPROGRAMS\Startup\tray.lnk" "$INSTDIR\tray.exe"
  Exec '"$INSTDIR\tray.exe"'
SectionEnd

Section -AdditionalIcons
  WriteIniStr "$INSTDIR\${PRODUCT_NAME}.url" "InternetShortcut" "URL" "${PRODUCT_WEB_SITE}"
  CreateShortCut "$SMPROGRAMS\Twert\Website.lnk" "$INSTDIR\${PRODUCT_NAME}.url"
  CreateShortCut "$SMPROGRAMS\Twert\Uninstall.lnk" "$INSTDIR\uninst.exe"
SectionEnd

Section -Post
  WriteUninstaller "$INSTDIR\uninst.exe"
  WriteRegStr HKLM "${PRODUCT_DIR_REGKEY}" "" "$INSTDIR\nssm.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayName" "$(^Name)"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "UninstallString" "$INSTDIR\uninst.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayIcon" "$INSTDIR\nssm.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayVersion" "${PRODUCT_VERSION}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "URLInfoAbout" "${PRODUCT_WEB_SITE}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "Publisher" "${PRODUCT_PUBLISHER}"
SectionEnd


Function un.onUninstSuccess
  HideWindow
  MessageBox MB_ICONINFORMATION|MB_OK "$(^Name) was successfully removed from your computer."
FunctionEnd

Function un.onInit
  MessageBox MB_ICONQUESTION|MB_YESNO|MB_DEFBUTTON2 "Are you sure you want to completely remove $(^Name) and all of its components?" IDYES +2
  Abort
FunctionEnd

Section Uninstall
  ExecWait '"$INSTDIR\trayStopExe.bat"'
  ExecWait '"$INSTDIR\snifferStopService.bat"'
  ExecWait '"$INSTDIR\runStopService.bat"'
  Delete "$SMPROGRAMS\Startup\tray.lnk"
  Delete "$INSTDIR\${PRODUCT_NAME}.url"
  Delete "$INSTDIR\uninst.exe"
  Delete "$INSTDIR\trayStopExe.bat"
  Delete "$INSTDIR\tray.exe"
  Delete "$INSTDIR\snifferStopService.bat"
  Delete "$INSTDIR\snifferStartService.bat"
  Delete "$INSTDIR\sniffer.exe"
  Delete "$INSTDIR\runStopService.bat"
  Delete "$INSTDIR\runStartService.bat"
  Delete "$INSTDIR\run.exe"
  Delete "$INSTDIR\Prerequisites\npcap-1.71.exe"
  Delete "$INSTDIR\nssm.exe"
  Delete "$INSTDIR\nblocker.sqlite3"

  Delete "$SMPROGRAMS\Twert\Uninstall.lnk"
  Delete "$SMPROGRAMS\Twert\Website.lnk"
  Delete "$DESKTOP\Twert.lnk"
  Delete "$SMPROGRAMS\Twert\Twert.lnk"

  RMDir "$SMPROGRAMS\Twert"
  RMDir "$INSTDIR\Prerequisites"
  RMDir "$INSTDIR"

  DeleteRegKey ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}"
  DeleteRegKey HKLM "${PRODUCT_DIR_REGKEY}"
  SetAutoClose true
SectionEnd