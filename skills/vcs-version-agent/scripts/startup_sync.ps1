# PowerShell Startup Sync Script para o GabeBrain
# Executado no boot da maquina local para sincronizar projetos com GitHub e Arena.ai

$ErrorActionPreference = "SilentlyContinue"
$pythonPath = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $pythonPath) {
    $pythonPath = "C:\Users\Gabriel\AppData\Local\Programs\Python\Python314\python.exe"
}

$agentScript = "C:\Users\Gabriel\.gemini\config\skills\vcs-version-agent\scripts\vcs_agent.py"
$logFile = "C:\Users\Gabriel\.gemini\antigravity\logs\vcs_sync.log"

# Aguarda até 15 segundos para estabilização de rede (WiFi / Ethernet)
$retries = 5
$connected = $false
while ($retries -gt 0 -and -not $connected) {
    try {
        $tcp = New-Object System.Net.Sockets.TcpClient
        $iar = $tcp.BeginConnect("github.com", 443, $null, $null)
        $wait = $iar.AsyncWaitHandle.WaitOne(2000, $false)
        if ($wait) {
            $tcp.EndConnect($iar)
            $connected = $true
        }
        $tcp.Close()
    } catch {
        $connected = $false
    }
    if (-not $connected) {
        Start-Sleep -Seconds 2
        $retries--
    }
}

# Executa o GabeBrain VCS Agent em modo startup
& $pythonPath $agentScript startup 2>&1 | Out-File -FilePath $logFile -Append -Encoding utf8
