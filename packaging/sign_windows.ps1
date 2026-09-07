param(
    [Parameter(Mandatory = $true)]
    [string]$Path,

    [Parameter(Mandatory = $true)]
    [string]$PfxPath,

    [Parameter(Mandatory = $true)]
    [string]$PfxPassword,

    [Parameter(Mandatory = $true)]
    [string]$ExpectedThumbprint,

    [Parameter(Mandatory = $true)]
    [ValidatePattern('^https://')]
    [string]$TimestampUrl
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

function Normalize-Thumbprint([string]$Value) {
    return (($Value -replace '[^0-9A-Fa-f]', '').ToUpperInvariant())
}

function Find-SignTool {
    $command = Get-Command signtool.exe -ErrorAction SilentlyContinue
    if ($null -ne $command) {
        return $command.Source
    }

    $kitsRoot = Join-Path ${env:ProgramFiles(x86)} 'Windows Kits\10\bin'
    if (Test-Path -LiteralPath $kitsRoot) {
        $candidate = Get-ChildItem -LiteralPath $kitsRoot -Directory -ErrorAction SilentlyContinue |
            Sort-Object Name -Descending |
            ForEach-Object { Join-Path $_.FullName 'x64\signtool.exe' } |
            Where-Object { Test-Path -LiteralPath $_ } |
            Select-Object -First 1
        if ($candidate) {
            return $candidate
        }
    }

    throw 'signtool.exe was not found on the Windows runner.'
}

if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
    throw "Executable not found: $Path"
}
if (-not (Test-Path -LiteralPath $PfxPath -PathType Leaf)) {
    throw "Signing PFX not found: $PfxPath"
}
if ([string]::IsNullOrWhiteSpace($PfxPassword)) {
    throw 'Signing PFX password is empty.'
}

$expected = Normalize-Thumbprint $ExpectedThumbprint
if ($expected.Length -lt 40) {
    throw 'Expected signing certificate thumbprint is missing or malformed.'
}

$existing = Get-ChildItem Cert:\CurrentUser\My | Where-Object {
    (Normalize-Thumbprint $_.Thumbprint) -eq $expected
}
if ($existing) {
    throw "Refusing to reuse a pre-existing certificate with thumbprint $expected on the runner."
}

$securePassword = ConvertTo-SecureString -String $PfxPassword -AsPlainText -Force
$imported = $null
try {
    $imported = Import-PfxCertificate \
        -FilePath $PfxPath \
        -CertStoreLocation Cert:\CurrentUser\My \
        -Password $securePassword \
        -Exportable:$false

    if ($null -eq $imported) {
        throw 'PFX import returned no certificate.'
    }

    $actual = Normalize-Thumbprint $imported.Thumbprint
    if ($actual -ne $expected) {
        throw "Signing certificate thumbprint mismatch. Expected $expected but imported $actual."
    }

    $codeSigningOid = '1.3.6.1.5.5.7.3.3'
    $hasCodeSigningEku = $false
    foreach ($extension in $imported.Extensions) {
        if ($extension -is [System.Security.Cryptography.X509Certificates.X509EnhancedKeyUsageExtension]) {
            foreach ($oid in $extension.EnhancedKeyUsages) {
                if ($oid.Value -eq $codeSigningOid) {
                    $hasCodeSigningEku = $true
                    break
                }
            }
        }
        if ($hasCodeSigningEku) { break }
    }
    if (-not $hasCodeSigningEku) {
        throw 'Configured signing certificate does not include the Code Signing EKU.'
    }

    if (-not $imported.HasPrivateKey) {
        throw 'Configured signing certificate does not expose a private key after import.'
    }

    $signTool = Find-SignTool
    & $signTool sign /fd SHA256 /sha1 $expected /tr $TimestampUrl /td SHA256 /v $Path
    if ($LASTEXITCODE -ne 0) {
        throw "signtool.exe failed with exit code $LASTEXITCODE."
    }

    Write-Host "Windows executable signed with configured certificate thumbprint $expected."
}
finally {
    if ($null -ne $imported) {
        $storePath = "Cert:\CurrentUser\My\$($imported.Thumbprint)"
        if (Test-Path -LiteralPath $storePath) {
            Remove-Item -LiteralPath $storePath -Force
        }
    }
}
