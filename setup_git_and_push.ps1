# Git Setup and Push Script for Vibe Search
# This script will initialize git, add all files, and push to GitHub

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Git Setup and Push to GitHub" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check if git is installed
try {
    $gitVersion = git --version 2>&1
    Write-Host "Git found: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Git is not installed!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Git first:" -ForegroundColor Yellow
    Write-Host "1. Download from: https://git-scm.com/download/win" -ForegroundColor Yellow
    Write-Host "2. Or install via winget: winget install Git.Git" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "After installing Git, restart PowerShell and run this script again." -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Step 1: Updating README.md..." -ForegroundColor Cyan
# Update README.md with the header
$readmeContent = "# Vibe_search`n`n"
$readmeContent += Get-Content "README.md" -Raw -ErrorAction SilentlyContinue
if ($readmeContent) {
    # If README exists, prepend the header
    $readmeContent = "# Vibe_search`n`n" + $readmeContent
} else {
    $readmeContent = "# Vibe_search`n"
}
Set-Content -Path "README.md" -Value $readmeContent -NoNewline
Write-Host "✓ README.md updated" -ForegroundColor Green

Write-Host ""
Write-Host "Step 2: Initializing Git repository..." -ForegroundColor Cyan
if (Test-Path ".git") {
    Write-Host "Git repository already initialized" -ForegroundColor Yellow
} else {
    git init
    Write-Host "✓ Git repository initialized" -ForegroundColor Green
}

Write-Host ""
Write-Host "Step 3: Adding all files..." -ForegroundColor Cyan
git add .
Write-Host "✓ All files added to staging" -ForegroundColor Green

Write-Host ""
Write-Host "Step 4: Creating initial commit..." -ForegroundColor Cyan
git commit -m "first commit"
Write-Host "✓ Initial commit created" -ForegroundColor Green

Write-Host ""
Write-Host "Step 5: Setting branch to main..." -ForegroundColor Cyan
git branch -M main
Write-Host "✓ Branch set to main" -ForegroundColor Green

Write-Host ""
Write-Host "Step 6: Adding remote origin..." -ForegroundColor Cyan
# Remove existing remote if it exists
git remote remove origin 2>$null
git remote add origin https://github.com/Mohit05agg/Vibe_search.git
Write-Host "✓ Remote origin added" -ForegroundColor Green

Write-Host ""
Write-Host "Step 7: Pushing to GitHub..." -ForegroundColor Cyan
Write-Host "This may prompt for GitHub credentials..." -ForegroundColor Yellow
Write-Host ""

try {
    git push -u origin main
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Green
    Write-Host "SUCCESS! All files pushed to GitHub!" -ForegroundColor Green
    Write-Host "==========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Repository URL: https://github.com/Mohit05agg/Vibe_search" -ForegroundColor Cyan
} catch {
    Write-Host ""
    Write-Host "ERROR: Push failed!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Possible issues:" -ForegroundColor Yellow
    Write-Host "1. GitHub authentication required" -ForegroundColor Yellow
    Write-Host "   - Use GitHub Personal Access Token" -ForegroundColor Yellow
    Write-Host "   - Or use GitHub Desktop" -ForegroundColor Yellow
    Write-Host "2. Repository doesn't exist on GitHub" -ForegroundColor Yellow
    Write-Host "   - Create it at: https://github.com/new" -ForegroundColor Yellow
    Write-Host "   - Name: Vibe_search" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To push manually, run:" -ForegroundColor Cyan
    Write-Host "  git push -u origin main" -ForegroundColor White
}

Write-Host ""
Write-Host "Done!" -ForegroundColor Green

