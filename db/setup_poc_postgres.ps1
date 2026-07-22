$ErrorActionPreference = "Stop"

$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$data = Join-Path $PSScriptRoot "pgdata"
$pwFile = Join-Path $PSScriptRoot "pgpass_setup.tmp"
$dbName = "techknosite_reports"
$dbUser = "techknosite_bot"
$dbPassword = "TechknoSiteBot2026"
$dbPort = "5433"
$pgBin = "C:\Program Files\PostgreSQL\18\bin"

Set-Content -LiteralPath $pwFile -Value $dbPassword -NoNewline -Encoding ASCII
try {
    if (!(Test-Path -LiteralPath (Join-Path $data "PG_VERSION"))) {
        & (Join-Path $pgBin "initdb.exe") -D $data --username=$dbUser --pwfile=$pwFile --auth-host=scram-sha-256 --auth-local=scram-sha-256 -E UTF8
    }
}
finally {
    if (Test-Path -LiteralPath $pwFile) {
        Remove-Item -LiteralPath $pwFile -Force
    }
}

& (Join-Path $pgBin "pg_ctl.exe") -D $data status 2>&1 | Out-Null
$statusExit = $LASTEXITCODE
if ($statusExit -ne 0) {
    & (Join-Path $pgBin "pg_ctl.exe") -D $data -l (Join-Path $data "server.log") -o "-p $dbPort" start
    Start-Sleep -Seconds 2
}

$env:PGPASSWORD = $dbPassword
$exists = ((& (Join-Path $pgBin "psql.exe") -h localhost -p $dbPort -U $dbUser -d postgres -Atc "SELECT 1 FROM pg_database WHERE datname = '$dbName'") | Select-Object -First 1).Trim()
if ($exists -ne "1") {
    & (Join-Path $pgBin "createdb.exe") -h localhost -p $dbPort -U $dbUser $dbName
}

& (Join-Path $pgBin "psql.exe") -h localhost -p $dbPort -U $dbUser -d $dbName -c "SELECT current_database(), current_user;"
