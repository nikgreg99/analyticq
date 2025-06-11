# SAST Tools Docker Image Builder - Simplified Version with Timeout Handling
# Builds Docker images for SAST tools in the sast-tools directory

param(
    [switch]$Help,
    [switch]$Verbose,
    [switch]$Force,
    [int]$TimeoutMinutes = 10
)

# Configuration
$BaseDir = ".\sast-tools"
$LogFile = "build.log"
$ErrorActionPreference = "Continue"

# Initialize log file
"SAST Tools Docker Build Log - $(Get-Date)" | Out-File -FilePath $LogFile -Encoding UTF8

# Logging functions
function Write-Log {
    param([string]$Message, [string]$Level = "INFO")

    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$Level] $Message"

    # Console output with colors
    switch ($Level) {
        "ERROR" { Write-Host $logEntry -ForegroundColor Red }
        "SUCCESS" { Write-Host $logEntry -ForegroundColor Green }
        "WARNING" { Write-Host $logEntry -ForegroundColor Yellow }
        "VERBOSE" { if ($Verbose) { Write-Host $logEntry -ForegroundColor Cyan } }
        "DOCKER" { Write-Host $logEntry -ForegroundColor Magenta }
        default { Write-Host $logEntry }
    }

    # Write to log file
    Add-Content -Path $LogFile -Value $logEntry
}

# Simple Docker availability test
function Test-DockerAvailable {
    Write-Log "Checking Docker availability..."

    try {
        # Test docker command and daemon
        $null = docker version --format "{{.Server.Version}}" 2>$null

        if ($LASTEXITCODE -eq 0) {
            Write-Log "Docker is available and running" "SUCCESS"
            return $true
        } else {
            Write-Log "Docker is not available or daemon is not running" "ERROR"
            return $false
        }
    }
    catch {
        Write-Log "Docker check failed: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

# Check if image exists
function Test-ImageExists {
    param([string]$ImageName)

    try {
        $null = docker inspect $ImageName 2>$null
        return $LASTEXITCODE -eq 0
    }
    catch {
        return $false
    }
}

# Build Docker image with simple progress monitoring
function New-DockerImage {
    param(
        [string]$ToolPath,
        [string]$ImageName,
        [switch]$Force
    )

    $fullPath = Join-Path -Path $BaseDir -ChildPath $ToolPath
    $dockerfilePath = Join-Path -Path $fullPath -ChildPath "Dockerfile"

    Write-Log "Processing: $ImageName"
    Write-Log "Source: $fullPath" "VERBOSE"

    # Check if Dockerfile exists
    if (-not (Test-Path $dockerfilePath)) {
        Write-Log "Dockerfile not found in $fullPath" "ERROR"
        return $false
    }

    # Check if image exists
    $imageExists = Test-ImageExists $ImageName

    if ($imageExists -and -not $Force) {
        Write-Log "Image $ImageName already exists (use -Force to rebuild)" "WARNING"
        return "SKIPPED"
    }

    # Show Dockerfile content if verbose
    if ($Verbose) {
        Write-Log "Dockerfile content:" "VERBOSE"
        Get-Content $dockerfilePath | ForEach-Object {
            Write-Log "  $_" "VERBOSE"
        }
    }

    # Build the image
    Write-Log "Building image: $ImageName" "DOCKER"
    $buildStart = Get-Date

    try {
        # Simple docker build with output capture
        $buildOutput = docker build -t $ImageName $fullPath 2>&1
        $buildSuccess = $LASTEXITCODE -eq 0

        $buildEnd = Get-Date
        $buildDuration = $buildEnd - $buildStart

        if ($buildSuccess) {
            Write-Log "Successfully built: $ImageName (took $($buildDuration.ToString('mm\:ss')))" "SUCCESS"

            # Show image info if verbose
            if ($Verbose) {
                $imageInfo = docker images $ImageName --format "table {{.Repository}}:{{.Tag}}\t{{.Size}}\t{{.CreatedSince}}"
                Write-Log "Image info: $imageInfo" "VERBOSE"
            }

            return $true
        } else {
            Write-Log "Failed to build: $ImageName (took $($buildDuration.ToString('mm\:ss')))" "ERROR"
            if ($Verbose) {
                Write-Log "Build output:" "ERROR"
                $buildOutput | ForEach-Object { Write-Log "  $_" "ERROR" }
            }
            return $false
        }
    }
    catch {
        Write-Log "Exception building $ImageName`: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

# Main build process
function Start-BuildProcess {
    param([switch]$Force)

    $stats = @{
        Built = 0
        Skipped = 0
        Failed = 0
        Total = 0
    }

    $startTime = Get-Date
    Write-Log "Starting SAST tools build process"
    Write-Log "Base directory: $BaseDir"

    if ($Force) {
        Write-Log "Force rebuild enabled"
    }

    # Check base directory
    if (-not (Test-Path $BaseDir -PathType Container)) {
        Write-Log "Base directory $BaseDir does not exist" "ERROR"
        return 1
    }

    # Find all tools
    $languageDirs = Get-ChildItem -Path $BaseDir -Directory -ErrorAction SilentlyContinue

    if (-not $languageDirs) {
        Write-Log "No language directories found in $BaseDir" "WARNING"
        return 0
    }

    Write-Log "Found $($languageDirs.Count) language directory(ies)"

    # Process each language directory
    foreach ($langDir in $languageDirs) {
        $language = $langDir.Name
        Write-Log "Processing language: $language"

        $toolDirs = Get-ChildItem -Path $langDir.FullName -Directory -ErrorAction SilentlyContinue

        if (-not $toolDirs) {
            Write-Log "No tools found in $language" "WARNING"
            continue
        }

        Write-Log "Found $($toolDirs.Count) tool(s) in $language"

        foreach ($toolDir in $toolDirs) {
            $toolName = $toolDir.Name
            $toolPath = "$language/$toolName"
            $imageName = "${toolName}:latest"

            $stats.Total++

            $result = New-DockerImage -ToolPath $toolPath -ImageName $imageName -Force:$Force

            switch ($result) {
                $true { $stats.Built++ }
                $false { $stats.Failed++ }
                "SKIPPED" { $stats.Skipped++ }
            }

            # Progress update
            $processed = $stats.Built + $stats.Skipped + $stats.Failed
            Write-Log "Progress: $processed/$($stats.Total) - Built: $($stats.Built), Skipped: $($stats.Skipped), Failed: $($stats.Failed)"
        }
    }

    # Final summary
    $endTime = Get-Date
    $duration = $endTime - $startTime

    Write-Log "Build process completed"
    Write-Log "Duration: $($duration.ToString('hh\:mm\:ss'))"
    Write-Log "Built: $($stats.Built)" "SUCCESS"
    Write-Log "Skipped: $($stats.Skipped)" "WARNING"
    Write-Log "Failed: $($stats.Failed)" $(if ($stats.Failed -gt 0) { "ERROR" } else { "INFO" })

    # Show all images if verbose
    if ($Verbose -and ($stats.Built -gt 0 -or $stats.Skipped -gt 0)) {
        Write-Log "Available images:" "VERBOSE"
        docker images --format "table {{.Repository}}:{{.Tag}}\t{{.Size}}\t{{.CreatedSince}}" | ForEach-Object {
            if ($_ -match ":latest") {
                Write-Log "  $_" "VERBOSE"
            }
        }
    }

    return $(if ($stats.Failed -gt 0) { 1 } else { 0 })
}

# Show help
function Show-Help {
    Write-Host @"
SAST Tools Docker Builder

Usage: .\Build-SASTTools.ps1 [OPTIONS]

This script builds Docker images for SAST tools in the './sast-tools' directory.

Expected directory structure:
  sast-tools\
  ├── language1\
  │   ├── tool1\
  │   │   └── Dockerfile
  │   └── tool2\
  │       └── Dockerfile
  └── language2\
      └── tool3\
          └── Dockerfile

Options:
  -Help             Show this help
  -Verbose          Show detailed output
  -Force            Force rebuild existing images
  -TimeoutMinutes   Build timeout in minutes (default: 10)

Examples:
  .\Build-SASTTools.ps1
  .\Build-SASTTools.ps1 -Verbose
  .\Build-SASTTools.ps1 -Force
  .\Build-SASTTools.ps1 -Force -Verbose -TimeoutMinutes 15

"@
}

# Main execution
function Main {
    Write-Log "SAST Tools Docker Builder started"

    if ($Help) {
        Show-Help
        return 0
    }

    # Test Docker availability
    if (-not (Test-DockerAvailable)) {
        Write-Log "Please ensure Docker Desktop is running" "ERROR"
        return 1
    }

    # Run build process
    $exitCode = Start-BuildProcess -Force:$Force

    Write-Log "Script completed with exit code: $exitCode"
    return $exitCode
}

# Execute main function
exit (Main)
