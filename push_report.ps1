# push_report.ps1 — committeten Report auf GitHub pushen
# Verwendung: .\push_report.ps1 (aus dem Repo-Root)
#
# Liest GITHUB_TOKEN aus .env (Classic PAT mit 'repo'-Scope).
# Erstellt Branch claude/report-<heute>, pusht und gibt PR-URL aus.

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
$branch  = "claude/report-$Date"
$report  = "reports/report_$Date.md"

# Remote temporär mit Token setzen (wird nicht committed)
git remote set-url origin $remote

# Sicherstellen dass Report committed ist
if (-not (Test-Path (Join-Path $PSScriptRoot $report))) {
    Write-Error "Report $report nicht gefunden."
    exit 1
}

git add $report
$status = git status --porcelain $report
if ($status) {
    git commit -m "report: daily market analysis $Date"
}

# Branch erstellen und pushen
$existingBranch = git branch --list $branch
if (-not $existingBranch) {
    git checkout -b $branch
} else {
    git checkout $branch
}

git push -u origin $branch
Write-Host ""
Write-Host "Push erfolgreich. PR erstellen unter:"
Write-Host "https://github.com/Melxnne/fundedelite-daily-routine/compare/$branch"

# Remote wieder auf HTTPS ohne Token setzen
git remote set-url origin "https://github.com/Melxnne/fundedelite-daily-routine.git"
