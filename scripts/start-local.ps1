param()

$ErrorActionPreference = 'Stop'
$projectRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$pythonPath = Join-Path $projectRoot '.venv\Scripts\python.exe'
$runtimePath = Join-Path $projectRoot '.runtime'
if (-not (Test-Path -LiteralPath $pythonPath)) { throw 'Create .venv and install requirements first; see README.md.' }
if (-not (Test-Path -LiteralPath (Join-Path $projectRoot '.env'))) { throw 'Configure .env first; see README.md.' }

function Test-LocalPort([int]$Port) {
    $client = New-Object System.Net.Sockets.TcpClient
    try {
        $task = $client.ConnectAsync('127.0.0.1', $Port)
        if (-not $task.Wait(500)) { return $false }
        return $client.Connected
    } catch { return $false }
    finally { $client.Dispose() }
}

Push-Location -LiteralPath $projectRoot
try {
    $metadata = & $pythonPath -c "import json; from dotenv import dotenv_values; c=dotenv_values('.env'); print(json.dumps({k:c.get(k) for k in ('APP_MODE','MYSQL_HOST','MYSQL_PORT')}))"
    if ($LASTEXITCODE -ne 0) { throw 'Could not read the local configuration.' }
    $config = $metadata | ConvertFrom-Json
    if ($config.APP_MODE -eq 'live') {
        $port = if ($config.MYSQL_PORT) { [int]$config.MYSQL_PORT } else { 3306 }
        if ($config.MYSQL_HOST -in @('127.0.0.1', 'localhost') -and -not (Test-LocalPort $port)) {
            $mysqlBase = Join-Path $runtimePath 'mysql-8.4.13-winx64'
            $mysqlBinary = Join-Path $mysqlBase 'bin\mysqld.exe'
            $mysqlData = Join-Path $runtimePath 'mysql-data'
            if ($port -ne 3307 -or -not (Test-Path -LiteralPath $mysqlBinary) -or -not (Test-Path -LiteralPath $mysqlData)) {
                throw "Start your MySQL server on port $port before starting the app."
            }
            $mysqlArgs = @('--no-defaults', ('--basedir="' + $mysqlBase + '"'), ('--datadir="' + $mysqlData + '"'), '--bind-address=127.0.0.1', '--port=3307', '--mysqlx=OFF', '--console')
            Start-Process -FilePath $mysqlBinary -ArgumentList $mysqlArgs -WorkingDirectory $projectRoot -WindowStyle Hidden -RedirectStandardOutput (Join-Path $runtimePath 'mysql.stdout.log') -RedirectStandardError (Join-Path $runtimePath 'mysql.stderr.log') | Out-Null
            for ($attempt = 0; $attempt -lt 30 -and -not (Test-LocalPort $port); $attempt++) { Start-Sleep -Milliseconds 500 }
            if (-not (Test-LocalPort $port)) { throw 'MySQL did not become ready. Check .runtime/mysql.stderr.log.' }
        }
        & $pythonPath -m flask --app app check-db
        if ($LASTEXITCODE -ne 0) { throw 'The configured database is not ready; the app was not started.' }
    }
    if (-not (Test-LocalPort 5000)) {
        New-Item -ItemType Directory -Force -Path $runtimePath | Out-Null
        Start-Process -FilePath $pythonPath -ArgumentList @('-u', 'app.py') -WorkingDirectory $projectRoot -WindowStyle Hidden -RedirectStandardOutput (Join-Path $runtimePath 'flask.stdout.log') -RedirectStandardError (Join-Path $runtimePath 'flask.stderr.log') | Out-Null
        for ($attempt = 0; $attempt -lt 30 -and -not (Test-LocalPort 5000); $attempt++) { Start-Sleep -Milliseconds 500 }
        if (-not (Test-LocalPort 5000)) { throw 'Flask did not become ready. Check .runtime/flask.stderr.log.' }
    }
    Write-Output 'Dina''s Laundry is available at http://127.0.0.1:5000'
    Write-Output ('Booking mode: ' + $config.APP_MODE)
} finally { Pop-Location }
