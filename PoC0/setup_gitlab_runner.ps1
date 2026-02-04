# Configuration
$GITLAB_SERVER_CONTAINER = "gitlab-server"
$GITLAB_RUNNER_CONTAINER = "gitlab-runner"
$RUNNER_DESCRIPTION = "Docker-Runner-PoC"
$RUNNER_EXECUTOR = "docker"
$DOCKER_IMAGE = "python:3.11"
$RUBY_SCRIPT_LOCAL = "gen_token.rb"
$RUBY_SCRIPT_REMOTE = "/tmp/gen_token.rb"

Write-Host "=== GitLab Runner Registration Automation ==="

# 1. Generate Runner Token
Write-Host "1. Generating Runner Token..."

# Ruby script content to generate token
$rubyScriptContent = @"
r=Ci::Runner.new
r.runner_type='instance_type'
r.description='$RUNNER_DESCRIPTION'
r.tag_list=['docker', 'shadow-file']
r.run_untagged=true
r.locked=false
r.access_level='not_protected'
r.save!
print r.token
"@

# Create Ruby script locally
Set-Content -Path $RUBY_SCRIPT_LOCAL -Value $rubyScriptContent -Encoding Ascii -NoNewline

# Copy to container
docker cp $RUBY_SCRIPT_LOCAL "$($GITLAB_SERVER_CONTAINER):$RUBY_SCRIPT_REMOTE"

if ($LASTEXITCODE -ne 0) {
    Write-Error "Error: Failed to copy script to container. Is gitlab-server running?"
    exit 1
}

# Execute script to get token
Write-Host "   Executing token generation script in container..."
$RUNNER_TOKEN = docker exec $GITLAB_SERVER_CONTAINER gitlab-rails runner $RUBY_SCRIPT_REMOTE 2>$null
if ($RUNNER_TOKEN) {
    # Trim whitespace and potential carriage returns
    $RUNNER_TOKEN = $RUNNER_TOKEN.Trim()
}

# Clean up remote script
docker exec $GITLAB_SERVER_CONTAINER rm $RUBY_SCRIPT_REMOTE

if (-not $RUNNER_TOKEN) {
    Write-Error "Error: Failed to generate runner token. Check if GitLab is running."
    exit 1
}
Write-Host "   Token generated: $RUNNER_TOKEN"

# 2. Detect Docker Network
Write-Host "2. Detecting Docker Network..."
# Resolve the actual container ID
$GITLAB_SERVER_CONTAINER_ID = docker compose ps -q $GITLAB_SERVER_CONTAINER
if ($GITLAB_SERVER_CONTAINER_ID) {
    $GITLAB_SERVER_CONTAINER_ID = $GITLAB_SERVER_CONTAINER_ID.Trim()
}

if (-not $GITLAB_SERVER_CONTAINER_ID) {
    Write-Error "Error: Could not resolve container ID for service '$GITLAB_SERVER_CONTAINER'."
    exit 1
}

# Inspect network
$NETWORK_NAME = docker inspect $GITLAB_SERVER_CONTAINER_ID --format '{{range $k, $v := .NetworkSettings.Networks}}{{$k}}{{end}}'
if ($NETWORK_NAME) {
    $NETWORK_NAME = $NETWORK_NAME.Trim()
}

if (-not $NETWORK_NAME) {
    Write-Warning "Warning: Could not detect network name. Defaulting to 'gitlab-net'."
    $NETWORK_NAME = "gitlab-net"
} else {
    Write-Host "   Detected network: $NETWORK_NAME"
}

# 3. Register Runner
Write-Host "3. Registering Runner..."
docker compose exec $GITLAB_RUNNER_CONTAINER gitlab-runner register `
  --non-interactive `
  --url "http://$GITLAB_SERVER_CONTAINER" `
  --token "$RUNNER_TOKEN" `
  --executor "$RUNNER_EXECUTOR" `
  --docker-image "$DOCKER_IMAGE" `
  --docker-network-mode "$NETWORK_NAME" `
  --clone-url "http://$GITLAB_SERVER_CONTAINER" `
  --docker-volumes "/var/run/docker.sock:/var/run/docker.sock"

if ($LASTEXITCODE -eq 0) {
    Write-Host "=== Registration Completed Successfully ==="
    # Clean up local ruby script
    if (Test-Path $RUBY_SCRIPT_LOCAL) {
        Remove-Item $RUBY_SCRIPT_LOCAL
    }
} else {
    Write-Error "Error: Registration failed."
    exit 1
}
