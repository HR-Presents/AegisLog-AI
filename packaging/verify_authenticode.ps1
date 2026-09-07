param(
    [Parameter(Mandatory = $true)]
    [string]$Path,

    [string]$ExpectedThumbprint = '',

    [switch]$RequireTimestamp
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

function Normalize-Thumbprint([string]$Value) {
    return (($Value -replace '[^0-9A-Fa-f]', '').ToUpperInvariant())
}

if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
    throw "Executable not found: $Path"
}

$signature = Get-AuthenticodeSignature -LiteralPath $Path
if ($signature.Status -ne [System.Management.Automation.SignatureStatus]::Valid) {
    throw "Authenticode signature is not valid for '$Path' (status: $($signature.Status))."
}

if ($null -eq $signature.SignerCertificate) {
    throw "Authenticode signature has no signer certificate for '$Path'."
}

$codeSigningOid = "1.3.6.1.5.5.7.3.3"
$hasCodeSigningEku = $false
foreach ($extension in $signature.SignerCertificate.Extensions) {
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
    throw "Signer certificate for '$Path' does not include the Code Signing EKU."
}

if (-not [string]::IsNullOrWhiteSpace($ExpectedThumbprint)) {
    $expected = Normalize-Thumbprint $ExpectedThumbprint
    $actual = Normalize-Thumbprint $signature.SignerCertificate.Thumbprint
    if ($expected.Length -lt 40) {
        throw 'Expected signing certificate thumbprint is malformed.'
    }
    if ($actual -ne $expected) {
        throw "Signer certificate thumbprint mismatch. Expected $expected but found $actual."
    }
}

if ($RequireTimestamp -and $null -eq $signature.TimeStamperCertificate) {
    throw "Authenticode signature for '$Path' is not RFC3161 timestamped."
}

Write-Host "Valid Authenticode signature detected."
Write-Host "Signer: $($signature.SignerCertificate.Subject)"
Write-Host "Thumbprint: $($signature.SignerCertificate.Thumbprint)"
if ($null -ne $signature.TimeStamperCertificate) {
    Write-Host "Timestamp signer: $($signature.TimeStamperCertificate.Subject)"
}
