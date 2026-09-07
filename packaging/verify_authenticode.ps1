param(
    [Parameter(Mandatory = $true)]
    [string]$Path
)

$ErrorActionPreference = "Stop"

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

Write-Host "Valid Authenticode signature detected."
Write-Host "Signer: $($signature.SignerCertificate.Subject)"
Write-Host "Thumbprint: $($signature.SignerCertificate.Thumbprint)"
