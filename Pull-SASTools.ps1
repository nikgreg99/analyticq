# SAST Tools Image Puller - Download from GitHub Container Registry
# Downloads pre-built SAST tool images from GitHub private registry

param(
    [switch]$Help,
    [switch]$Verbose,
    [switch]$Force,
    [string]$Registry = "ghcr.io",
    [string]$Organization = "",
    [string]$Token = "",
    [string]$ConfigFile = "sast-tools-config.json",
    [int]$TimeoutMinutes = 5,
    [string[]]$ToolFilter = @()
)

# Configuration
$LogFile = "pull.log"
$ErrorActionPreference = "Continue"

# Initialize log file
"SAST Tools Image Pull Log - $(Get-Date)" | Out-File -FilePath $LogFile -Encoding UTF8

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

# Test Docker availability
function Test-DockerAvailable {
    Write-Log "Checking Docker availability..."

    try {
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

# Check if image exists locally
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

# Authenticate with GitHub Container Registry
function Connect-GitHubRegistry {
    param(
        [string]$Token,
        [string]$Registry = "ghcr.io"
    )

    if ([string]::IsNullOrWhiteSpace($Token)) {
        Write-Log "No token provided, attempting without authentication" "WARNING"
        return $true
    }

    Write-Log "Authenticating with $Registry..."

    try {
        # Use token as password with username (can be anything for GitHub)
        $Token | docker login $Registry --username "token" --password-stdin 2>$null

        if ($LASTEXITCODE -eq 0) {
            Write-Log "Successfully authenticated with $Registry" "SUCCESS"
            return $true
        } else {
            Write-Log "Authentication failed with $Registry" "ERROR"
            return $false
        }
    }
    catch {
        Write-Log "Authentication error: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

# Load configuration from JSON file
function Get-SASTToolsConfig {
    param([string]$ConfigFile)

    if (-not (Test-Path $ConfigFile)) {
        Write-Log "Config file $ConfigFile not found, using default configuration" "WARNING"
        return Get-DefaultConfig
    }

    try {
        $config = Get-Content $ConfigFile -Raw | ConvertFrom-Json
        Write-Log "Loaded configuration from $ConfigFile"
        return $config
    }
    catch {
        Write-Log "Failed to parse config file: $($_.Exception.Message)" "ERROR"
        Write-Log "Using default configuration" "WARNING"
        return Get-DefaultConfig
    }
}

# Default configuration
function Get-DefaultConfig {
    return @{
        tools = @(
            @{
                name = "bandit"
                language = "python"
                image = "bandit"
                tag = "latest"
            }
        )
    }
}

# Pull Docker image
function Get-DockerImage {
    param(
        [object]$Tool,
        [string]$Registry,
        [string]$Organization,
        [switch]$Force
    )

    $imageName = $Tool.image
    $tag = if ($Tool.tag) { $Tool.tag } else { "latest" }
    $localImageName = "${imageName}:${tag}"
    $remoteImageName = "${Registry}/${Organization}/${imageName}:${tag}"

    Write-Log "Processing: $($Tool.name) ($($Tool.language))"
    Write-Log "Remote image: $remoteImageName" "VERBOSE"

    # Check if image exists locally
    $imageExists = Test-ImageExists $localImageName

    if ($imageExists -and -not $Force) {
        Write-Log "Image $localImageName already exists locally (use -Force to re-pull)" "WARNING"
        return "SKIPPED"
    }

    # Pull the image
    Write-Log "Pulling image: $remoteImageName" "DOCKER"
    $pullStart = Get-Date

    try {
        # Pull image with progress
        $pullOutput = docker pull $remoteImageName 2>&1
        $pullSuccess = $LASTEXITCODE -eq 0

        if ($pullSuccess) {
            # Tag with local name if different
            if ($remoteImageName -ne $localImageName) {
                Write-Log "Tagging as: $localImageName" "DOCKER"
                docker tag $remoteImageName $localImageName
            }

            $pullEnd = Get-Date
            $pullDuration = $pullEnd - $pullStart

            Write-Log "Successfully pulled: $localImageName (took $($pullDuration.ToString('mm\:ss')))" "SUCCESS"

            # Show image info if verbose
            if ($Verbose) {
                $imageInfo = docker images $localImageName --format "table {{.Repository}}:{{.Tag}}\t{{.Size}}\t{{.CreatedSince}}"
                Write-Log "Image info: $imageInfo" "VERBOSE"
            }

            return $true
        } else {
            $pullEnd = Get-Date
            $pullDuration = $pullEnd - $pullStart

            Write-Log "Failed to pull: $remoteImageName (took $($pullDuration.ToString('mm\:ss')))" "ERROR"
            if ($Verbose) {
                Write-Log "Pull output:" "ERROR"
                $pullOutput | ForEach-Object { Write-Log "  $_" "ERROR" }
            }
            return $false
        }
    }
    catch {
        Write-Log "Exception pulling $remoteImageName`: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

# Main pull process
function Start-PullProcess {
    param(
        [string]$Registry,
        [string]$Organization,
        [string]$ConfigFile,
        [string[]]$ToolFilter,
        [switch]$Force
    )

    $stats = @{
        Pulled = 0
        Skipped = 0
        Failed = 0
        Total = 0
    }

    $startTime = Get-Date
    Write-Log "Starting SAST tools pull process"
    Write-Log "Registry: $Registry"
    Write-Log "Organization: $Organization"

    if ($Force) {
        Write-Log "Force re-pull enabled"
    }

    # Load configuration
    $config = Get-SASTToolsConfig -ConfigFile $ConfigFile
    $tools = $config.tools

    # Filter tools if specified
    if ($ToolFilter.Count -gt 0) {
        $tools = $tools | Where-Object { $_.name -in $ToolFilter -or $_.language -in $ToolFilter }
        Write-Log "Filtered to $($tools.Count) tools: $($ToolFilter -join ', ')"
    }

    if (-not $tools -or $tools.Count -eq 0) {
        Write-Log "No tools found to process" "WARNING"
        return 0
    }

    Write-Log "Found $($tools.Count) tool(s) to process"

    # Process each tool
    foreach ($tool in $tools) {
        $stats.Total++

        $result = Get-DockerImage -Tool $tool -Registry $Registry -Organization $Organization -Force:$Force

        switch ($result) {
            $true { $stats.Pulled++ }
            $false { $stats.Failed++ }
            "SKIPPED" { $stats.Skipped++ }
        }

        # Progress update
        $processed = $stats.Pulled + $stats.Skipped + $stats.Failed
        Write-Log "Progress: $processed/$($stats.Total) - Pulled: $($stats.Pulled), Skipped: $($stats.Skipped), Failed: $($stats.Failed)"
    }

    # Final summary
    $endTime = Get-Date
    $duration = $endTime - $startTime

    Write-Log "Pull process completed"
    Write-Log "Duration: $($duration.ToString('hh\:mm\:ss'))"
    Write-Log "Pulled: $($stats.Pulled)" "SUCCESS"
    Write-Log "Skipped: $($stats.Skipped)" "WARNING"
    Write-Log "Failed: $($stats.Failed)" $(if ($stats.Failed -gt 0) { "ERROR" } else { "INFO" })

    # Show all SAST images if verbose
    if ($Verbose -and ($stats.Pulled -gt 0 -or $stats.Skipped -gt 0)) {
        Write-Log "Available SAST tool images:" "VERBOSE"
        $tools | ForEach-Object {
            $imageName = "$($_.image):$(if ($_.tag) { $_.tag } else { 'latest' })"
            if (Test-ImageExists $imageName) {
                $imageInfo = docker images $imageName --format "{{.Repository}}:{{.Tag}}\t{{.Size}}\t{{.CreatedSince}}"
                Write-Log "  $imageInfo" "VERBOSE"
            }
        }
    }

    return $(if ($stats.Failed -gt 0) { 1 } else { 0 })
}

# Create sample configuration file
function New-ConfigFile {
    param([string]$ConfigFile)

    $sampleConfig = @{
        tools = @(
            @{
                name = "bandit"
                language = "python"
                image = "bandit"
                tag = "latest"
            }
        )
    } | ConvertTo-Json -Depth 3

    $sampleConfig | Out-File -FilePath $ConfigFile -Encoding UTF8
    Write-Log "Created sample configuration file: $ConfigFile" "SUCCESS"
}

# Show help
function Show-Help {
    Write-Host @"
SAST Tools Image Puller

Usage: .\Pull-SASTTools.ps1 [OPTIONS]

This script pulls pre-built SAST tool Docker images from GitHub Container Registry.

Options:
  -Help               Show this help
  -Verbose            Show detailed output
  -Force              Force re-pull existing images
  -Registry           Registry URL (default: ghcr.io)
  -Organization       GitHub organization/username (required)
  -Token              GitHub Personal Access Token for private registry
  -ConfigFile         Configuration file path (default: sast-tools-config.json)
  -TimeoutMinutes     Pull timeout in minutes (default: 5)
  -ToolFilter         Filter specific tools or languages (array)

Environment Variables:
  GITHUB_TOKEN        GitHub token (alternative to -Token parameter)
  SAST_REGISTRY_ORG   GitHub organization (alternative to -Organization)

Examples:
  # Basic usage
  .\Pull-SASTTools.ps1 -Organization "myorg" -Token "ghp_xxxx"

  # Using environment variables
  $env:GITHUB_TOKEN = "ghp_xxxx"
  $env:SAST_REGISTRY_ORG = "myorg"
  .\Pull-SASTTools.ps1

  # Pull specific tools
  .\Pull-SASTTools.ps1 -Organization "myorg" -ToolFilter @("bandit", "semgrep")

  # Force re-pull with verbose output
  .\Pull-SASTTools.ps1 -Organization "myorg" -Force -Verbose

  # Create sample config file
  .\Pull-SASTTools.ps1 -Help > /dev/null && echo '{}' | Out-File sast-tools-config.json

Configuration File Format (sast-tools-config.json):
{
  "tools": [
    {
      "name": "bandit",
      "language": "python",
      "image": "bandit",
      "tag": "latest"
    }
  ]
}

"@
}

# Main execution
function Main {
    Write-Log "SAST Tools Image Puller started"

    if ($Help) {
        Show-Help
        return 0
    }

    # Get organization from environment if not provided
    if ([string]::IsNullOrWhiteSpace($Organization)) {
        $Organization = $env:SAST_REGISTRY_ORG
        if ([string]::IsNullOrWhiteSpace($Organization)) {
            Write-Log "Organization must be specified via -Organization parameter or SAST_REGISTRY_ORG environment variable" "ERROR"
            Write-Log "Use -Help for more information" "INFO"
            return 1
        }
    }

    # Get token from environment if not provided
    if ([string]::IsNullOrWhiteSpace($Token)) {
        $Token = $env:GITHUB_TOKEN
    }

    Write-Log "Target: $Registry/$Organization"

    # Test Docker availability
    if (-not (Test-DockerAvailable)) {
        Write-Log "Please ensure Docker Desktop is running" "ERROR"
        return 1
    }

    # Authenticate with registry
    if (-not (Connect-GitHubRegistry -Token $Token -Registry $Registry)) {
        Write-Log "Failed to authenticate with registry" "ERROR"
        return 1
    }

    # Create sample config if it doesn't exist
    if (-not (Test-Path $ConfigFile)) {
        Write-Log "Configuration file not found, creating sample: $ConfigFile" "WARNING"
        New-ConfigFile -ConfigFile $ConfigFile
    }

    # Run pull process
    $exitCode = Start-PullProcess -Registry $Registry -Organization $Organization -ConfigFile $ConfigFile -ToolFilter $ToolFilter -Force:$Force

    Write-Log "Script completed with exit code: $exitCode"
    return $exitCode
}

# Execute main function
exit (Main)
