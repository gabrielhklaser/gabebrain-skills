# PowerShell Startup Status Check para o GabeBrain
# Executado no logon para verificar divergências sem commitar, fazer pull ou push.

$ErrorActionPreference = "SilentlyContinue"
$pythonCommand = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCommand) {
    Write-Error "Python nao foi encontrado no PATH."
    exit 1
}
$pythonPath = $pythonCommand.Source
$agentScript = Join-Path $PSScriptRoot "vcs_agent.py"
$logDir = Join-Path $HOME ".gemini\antigravity\logs"
$logFile = Join-Path $logDir "vcs_sync.log"
New-Item -ItemType Directory -Path $logDir -Force | Out-Null

# Aguarda ate 15 segundos para estabilizacao de rede (WiFi / Ethernet)
$retries = 5
$connected = $false
while ($retries -gt 0 -and -not $connected) {
    try {
        $result = Test-NetConnection -ComputerName "github.com" -Port 443 -WarningAction SilentlyContinue -InformationLevel Quiet
        if ($result) {
            $connected = $true
        }
    } catch {
        $connected = $false
    }
    if (-not $connected) {
        Start-Sleep -Seconds 2
        $retries--
    }
}

# Executa a verificação de status; nenhuma alteração de trabalho é sincronizada.
& $pythonPath $agentScript startup 2>&1 | Out-File -FilePath $logFile -Append -Encoding utf8
