# agente_excel.ps1
# HTTP via PowerShell — no necesita que Python tenga acceso a red
# Python solo se llama para automatizar Excel localmente (COM/IPC local)

param(
    [string]$PythonPath = "python",
    [string]$ScriptDir  = "",
    [switch]$Config
)

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$ErrorActionPreference = "SilentlyContinue"

# En PCs de empresa, WinHTTP tiene proxy corporativo que bloquea IPs de red local.
# El navegador usa WinINet (proxy diferente, con bypass para LAN).
# Anulamos el proxy para esta sesion para que Invoke-RestMethod llegue directamente.
[System.Net.WebRequest]::DefaultWebProxy = $null

# Al ejecutar como ScriptBlock, $MyInvocation.MyCommand.Path queda vacio.
# El BAT pasa -ScriptDir explicitamente para evitar este problema.
if (-not $ScriptDir) {
    $ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
}
if (-not $ScriptDir) {
    $ScriptDir = $PSScriptRoot
}
if (-not $ScriptDir) {
    $ScriptDir = (Get-Location).Path
}
$configFile = Join-Path $ScriptDir "agente_config.json"
$pyScript   = Join-Path $scriptDir "baja_excel_agente.py"
$POLL_SEC   = 5

# ── Configuración ──────────────────────────────────────────────────────────────

function Get-AgentConfig {
    if (Test-Path $configFile) {
        try { return Get-Content $configFile -Raw -Encoding UTF8 | ConvertFrom-Json }
        catch {}
    }
    return $null
}

function Save-AgentConfig($url, $token) {
    $json = [PSCustomObject]@{ server_url = $url; token = $token } | ConvertTo-Json
    # Guardar sin BOM para evitar que ConvertFrom-Json falle silenciosamente
    [System.IO.File]::WriteAllText($configFile, $json, [System.Text.Encoding]::UTF8)
}

function Read-AgentConfig {
    Write-Host ""
    Write-Host ("=" * 60)
    Write-Host "  CONFIGURACION DEL AGENTE"
    Write-Host ("=" * 60)
    Write-Host "  Esta configuracion se guarda y no vuelve a pedirse."
    Write-Host ""
    Write-Host "  Ejemplo de URL: http://192.168.1.103:5000"
    $url = (Read-Host "  URL del servidor").Trim().TrimEnd("/")
    # Limpiar errores tipicos: puntos antes de ':', espacios, barras dobles
    $url = $url -replace '\.:', ':'
    $url = $url.Trim('.')
    if (-not $url.StartsWith("http")) { $url = "http://$url" }
    $token = (Read-Host "  Contrasena admin (o numero de usuario admin)").Trim()
    Save-AgentConfig $url $token
    Write-Host "  Configuracion guardada en agente_config.json"
    Write-Host ""
    return (Get-AgentConfig)
}

# ── HTTP helpers ───────────────────────────────────────────────────────────────

function Invoke-AgentGet($url, $token) {
    $hdrs = @{ Authorization = "Bearer $token" }
    return Invoke-RestMethod -Uri $url -Headers $hdrs -Method Get -TimeoutSec 10
}

function Invoke-AgentPost($url, $token, $body = @{}) {
    $hdrs = @{ Authorization = "Bearer $token"; "Content-Type" = "application/json" }
    $json = $body | ConvertTo-Json -Compress
    return Invoke-RestMethod -Uri $url -Headers $hdrs -Method Post -Body $json -TimeoutSec 10
}

# ── Inicio ─────────────────────────────────────────────────────────────────────

$cfg = Get-AgentConfig
if ($Config -or -not $cfg -or -not $cfg.server_url -or -not $cfg.token) {
    $cfg = Read-AgentConfig
}

$srv   = $cfg.server_url
$token = $cfg.token

Write-Host "  Verificando conexion con $srv ..."
try {
    $test = Invoke-AgentGet "$srv/api/agente/poll" $token
    if ($null -eq $test) { throw "Respuesta nula" }
    Write-Host "  Conexion OK"
} catch {
    Write-Host "  [ERROR] No se pudo conectar: $_"
    Write-Host ""
    Write-Host "  Comprueba que el servidor esta arriba y la URL es correcta."
    Write-Host "  Vuelve a ejecutar  AGENTE_EXCEL.bat --config  para cambiar la URL."
    Read-Host "  Pulsa Enter para salir"
    exit 1
}

Write-Host ""
Write-Host ("=" * 60)
Write-Host "  AGENTE en espera de solicitudes  (Ctrl+C para detener)"
Write-Host ("=" * 60)
Write-Host ""

# ── Bucle principal ────────────────────────────────────────────────────────────

while ($true) {
    try {
        $poll = Invoke-AgentGet "$srv/api/agente/poll" $token

        if ($poll -and $poll.hay_solicitud) {
            Write-Host "  [$(Get-Date -f 'HH:mm:ss')] Solicitud recibida — procesando..."

            Invoke-AgentPost "$srv/api/agente/iniciar" $token | Out-Null

            $data       = Invoke-AgentGet "$srv/api/agente/pendientes" $token
            $pendientes = @($data.pendientes)

            if ($pendientes.Count -eq 0) {
                Write-Host "  Sin bajas pendientes."
                Invoke-AgentPost "$srv/api/agente/completar" $token @{ salida = "Sin bajas pendientes" } | Out-Null
            } else {
                $total      = $pendientes.Count
                $procesados = 0
                $errores    = 0
                $log        = @()

                for ($i = 0; $i -lt $total; $i++) {
                    $m    = $pendientes[$i]
                    $n    = $i + 1
                    $desc = if ($m.descripcion) {
                        $m.descripcion.Substring(0, [Math]::Min(40, $m.descripcion.Length))
                    } else { "-" }

                    Write-Host "  [$n/$total] $($m.codigo)  ($($m.estado))  $desc"

                    # Comprobar si el admin canceló
                    $cancelR = Invoke-AgentGet "$srv/api/agente/cancelado" $token
                    if ($cancelR -and $cancelR.cancelado) {
                        Write-Host "  Detenido por el admin."
                        $log += "Detenido por admin tras $procesados/$total"
                        break
                    }

                    # Python SOLO hace Excel local (sin red — no le afecta el firewall)
                    & $PythonPath $pyScript --codigo $m.codigo --estado $m.estado
                    $ok = ($LASTEXITCODE -eq 0)

                    if ($ok) {
                        Invoke-AgentPost "$srv/api/agente/marcar_uno/$($m.id)" $token | Out-Null
                        $procesados++
                        Write-Host "         OK procesado."
                        $log += "[$n/$total] $($m.codigo) OK"
                    } else {
                        $errores++
                        Write-Host "         ERROR al procesar en Excel."
                        $log += "[$n/$total] $($m.codigo) ERROR"
                    }

                    Start-Sleep -Seconds 2
                }

                $resumen = "Procesados: $procesados/$total  Errores: $errores"
                $salida  = ($log -join "`n") + "`n$resumen"
                Invoke-AgentPost "$srv/api/agente/completar" $token @{ salida = $salida } | Out-Null
                Write-Host "  $resumen"
                Write-Host ""
            }

            Write-Host "  [$(Get-Date -f 'HH:mm:ss')] En espera de nueva solicitud..."

        } else {
            Write-Host -NoNewline "`r  [$(Get-Date -f 'HH:mm:ss')] Esperando solicitud...   "
        }

    } catch {
        Write-Host "  [!] Error en bucle: $_"
    }

    Start-Sleep -Seconds $POLL_SEC
}
