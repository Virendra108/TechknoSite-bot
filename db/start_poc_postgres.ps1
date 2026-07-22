$ErrorActionPreference = "Stop"

$data = Join-Path $PSScriptRoot "pgdata"
$pgBin = "C:\Program Files\PostgreSQL\18\bin"

& (Join-Path $pgBin "pg_ctl.exe") -D $data status 2>&1 | Out-Null
$statusExit = $LASTEXITCODE
if ($statusExit -ne 0) {
    & (Join-Path $pgBin "pg_ctl.exe") -D $data -l (Join-Path $data "server.log") -o "-p 5433" start
}
