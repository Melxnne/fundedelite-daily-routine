# push_report.ps1 — committeten Report auf GitHub pushen
# Verwendung: .\push_report.ps1 (aus dem Repo-Root)
#
# Liest GITHUB_TOKEN aus .env (Classic PAT mit 'repo'-Scope).
# Pusht direkt auf master, kein Feature-Branch, kein PR.

param(
    [string]$Date = (Get-Date -Format "yyyy-MM-dd")
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# --- .env lesen ---
$envFile = Join-Path $PSScriptRoot ".env"
if (Test-Path $envFile) {
    Get-Content $envFile | ForEach-Object {
        if ($_ -match "^\s*([^#=]+?)\s*=\s*(.+?)\s*$") {
            [System.Environment]::SetEnvironmentVariable($Matches[1], $Matches[2], "Process")
        }
    }
}

$token = $env:GITHUB_TOKEN
if (-not $token -or $token -eq "ghp_xxxxxxxxxxxxxxxxxxxx") {
    Write-Error @"
GITHUB_TOKEN nicht gesetzt oder noch Platzhalter.
Schritte:
  1. Gehe zu https://github.com/settings/tokens → 'Generate new token (classic)'
  2. Scope: repo (Vollzugriff)
  3. Füge in .env ein: GITHUB_TOKEN=ghp_deintoken
"@
    exit 1
}

$remote  = "https://${token}@github.com/Melxnne/fundedelite-daily-routine.git"
$report  = "reports/report_$Date.md"

# Remote temporär mit Token setzen (wird nicht committed)
git remote set-url origin $remote

# Sicherstellen dass Report committed ist
if (-not (Test-Path (Join-Path $PSScriptRoot $report))) {
    Write-Error "Report $report nicht gefunden."
    exit 1
}

# Auf master wechseln und aktuellen Stand holen
git fetch origin master
git checkout master
git pull origin master

git add $report
$status = git status --porcelain $report
if ($status) {
    git commit -m "report: daily market analysis $Date"
}

# Direkt auf master pushen, kein Feature-Branch, kein PR
git push origin master
Write-Host ""
Write-Host "Push erfolgreich direkt auf master:"
Write-Host "https://github.com/Melxnne/fundedelite-daily-routine/blob/master/$report"

# Remote wieder auf HTTPS ohne Token setzen
git remote set-url origin "https://github.com/Melxnne/fundedelite-daily-routine.git"
