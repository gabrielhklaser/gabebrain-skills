' GabeBrain VCS Agent - Verificação silenciosa de estado no logon do Windows
' O checkout pode ser configurado via GABEBRAIN_SKILLS_DIR.
Set WshShell = CreateObject("WScript.Shell")
Set FSO = CreateObject("Scripting.FileSystemObject")
strSkillsDir = WshShell.ExpandEnvironmentStrings("%GABEBRAIN_SKILLS_DIR%")
If strSkillsDir = "%GABEBRAIN_SKILLS_DIR%" Or strSkillsDir = "" Then
    strSkillsDir = WshShell.ExpandEnvironmentStrings("%USERPROFILE%") & "\.gemini\config\skills"
End If
strScript = FSO.BuildPath(FSO.BuildPath(FSO.BuildPath(strSkillsDir, "vcs-version-agent"), "scripts"), "startup_sync.ps1")
strCommand = "powershell.exe -NoProfile -WindowStyle Hidden -File """ & strScript & """"
WshShell.Run strCommand, 0, False
Set FSO = Nothing
Set WshShell = Nothing
