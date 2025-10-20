# Copy UHFF Project to WSL Script
# Run this in PowerShell as Administrator

param(
    [string]$WSLDistro = "Ubuntu",
    [string]$TargetDir = "uhff-app"
)

Write-Host "Copying UHFF project to WSL..." -ForegroundColor Green

# Source directory (your current project)
$SourceDir = "C:\Users\Kobyd\OneDrive\Documents\GitHub\ether"

# Check if source directory exists
if (-not (Test-Path $SourceDir)) {
    Write-Error "Source directory not found: $SourceDir"
    exit 1
}

# Get WSL username
$WSLUser = wsl whoami

if ([string]::IsNullOrEmpty($WSLUser)) {
    Write-Error "Could not determine WSL username. Make sure WSL is installed and running."
    exit 1
}

Write-Host "WSL User: $WSLUser" -ForegroundColor Yellow

# Target directory in WSL
$WSLTargetPath = "\\wsl$\$WSLDistro\home\$WSLUser\$TargetDir"

Write-Host "Copying from: $SourceDir" -ForegroundColor Cyan
Write-Host "Copying to: $WSLTargetPath" -ForegroundColor Cyan

# Create target directory if it doesn't exist
if (-not (Test-Path $WSLTargetPath)) {
    New-Item -ItemType Directory -Path $WSLTargetPath -Force
    Write-Host "Created directory: $WSLTargetPath" -ForegroundColor Green
}

# Copy files
try {
    Copy-Item -Path "$SourceDir\*" -Destination $WSLTargetPath -Recurse -Force
    Write-Host "✅ Files copied successfully!" -ForegroundColor Green
    
    # List copied files
    Write-Host "`nCopied files:" -ForegroundColor Yellow
    Get-ChildItem $WSLTargetPath | ForEach-Object { Write-Host "  $($_.Name)" }
    
    Write-Host "`nNext steps:" -ForegroundColor Cyan
    Write-Host "1. Open WSL terminal: wsl" -ForegroundColor White
    Write-Host "2. Navigate to project: cd ~/$TargetDir" -ForegroundColor White
    Write-Host "3. Run setup script: chmod +x setup_wsl_android.sh && ./setup_wsl_android.sh" -ForegroundColor White
    
} catch {
    Write-Error "Failed to copy files: $_"
    exit 1
}