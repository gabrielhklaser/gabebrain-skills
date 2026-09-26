' GabeBrain VCS Agent - Inicializador Silencioso do Windows Boot
' Executa a sincronizacao de versoes local <-> GitHub em segundo plano sem janela preta
Set WshShell = CreateObject("WScript.Shell")
strCommand = "powershell.exe -ExecutionPolicy Bypass -NoProfile -WindowStyle Hidden -File ""C:\Users\Gabriel\.gemini\config\skills\vcs-version-agent\scripts\startup_sync.ps1"""
WshShell.Run strCommand, 0, False
Set WshShell = Nothing
