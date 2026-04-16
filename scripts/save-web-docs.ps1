param(
    [Parameter(Mandatory = $true)]
    [string[]] $Urls,

    [string] $OutputDir = "docs"
)

$ErrorActionPreference = "Stop"

function Get-BrowserPath {
    $candidates = @(
        "C:\Program Files\Google\Chrome\Application\chrome.exe",
        "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        "C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    )

    foreach ($candidate in $candidates) {
        if (Test-Path -LiteralPath $candidate) {
            return $candidate
        }
    }

    throw "Chrome or Edge was not found in standard Windows install locations."
}

function Convert-ToSafeFileName {
    param([string] $Url)

    $uri = [System.Uri] $Url
    $name = ($uri.Host + $uri.AbsolutePath).Trim("/")
    $name = $name -replace "[^a-zA-Z0-9._-]+", "-"
    $name = $name.Trim("-")

    if ([string]::IsNullOrWhiteSpace($name)) {
        return "web-doc"
    }

    return $name
}

$browser = Get-BrowserPath
$resolvedOutputDir = Resolve-Path -LiteralPath $OutputDir -ErrorAction SilentlyContinue
if (-not $resolvedOutputDir) {
    New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
    $resolvedOutputDir = Resolve-Path -LiteralPath $OutputDir
}

foreach ($url in $Urls) {
    $safeName = Convert-ToSafeFileName -Url $url
    $pdfPath = Join-Path $resolvedOutputDir "$safeName.pdf"

    Write-Host "Saving $url -> $pdfPath"
    $args = @(
        "--headless=new",
        "--disable-gpu",
        "--no-pdf-header-footer",
        "--print-to-pdf=$pdfPath",
        $url
    )

    $process = Start-Process -FilePath $browser -ArgumentList $args -Wait -PassThru -NoNewWindow
    if ($process.ExitCode -ne 0) {
        throw "Browser PDF export failed for $url with exit code $($process.ExitCode)."
    }
}

Write-Host "Done. Re-run POST /ingest so Kortex indexes the new PDFs."
