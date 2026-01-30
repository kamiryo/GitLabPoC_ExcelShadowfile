#!/bin/bash

# Configuration
GITLAB_SERVER_CONTAINER="gitlab-server"
GITLAB_RUNNER_CONTAINER="gitlab-runner"
RUNNER_DESCRIPTION="Docker-Runner-PoC"
RUNNER_EXECUTOR="docker"
DOCKER_IMAGE="python:3.11"
RUBY_SCRIPT_LOCAL="gen_token.rb"
RUBY_SCRIPT_REMOTE="/tmp/gen_token.rb"

echo "=== GitLab Runner Registration Automation ==="

# 1. Generate Runner Token
echo "1. Generating Runner Token..."

# Create Ruby script locally
cat <<EOF > "$RUBY_SCRIPT_LOCAL"
r=Ci::Runner.new
r.runner_type='instance_type'
r.description='$RUNNER_DESCRIPTION'
r.tag_list=['docker', 'shadow-file']
r.run_untagged=true
r.locked=false
r.access_level='not_protected'
r.save!
print r.token
EOF

# Copy to container
docker cp "$RUBY_SCRIPT_LOCAL" "$GITLAB_SERVER_CONTAINER:$RUBY_SCRIPT_REMOTE"

if [ $? -ne 0 ]; then
    echo "Error: Failed to copy script to container. Is gitlab-server running?"
    exit 1
fi

# Execute script to get token
RUNNER_TOKEN=$(docker exec "$GITLAB_SERVER_CONTAINER" gitlab-rails runner "$RUBY_SCRIPT_REMOTE" 2>/dev/null | tr -d '\r')

# Clean up
docker exec "$GITLAB_SERVER_CONTAINER" rm "$RUBY_SCRIPT_REMOTE"

if [ -z "$RUNNER_TOKEN" ]; then
    echo "Error: Failed to generate runner token. Check if GitLab is running."
    exit 1
fi
echo "   Token generated: $RUNNER_TOKEN"

# 2. Detect Docker Network
echo "2. Detecting Docker Network..."
# Resolve the actual container ID
GITLAB_SERVER_CONTAINER_ID=$(docker compose ps -q $GITLAB_SERVER_CONTAINER)

if [ -z "$GITLAB_SERVER_CONTAINER_ID" ]; then
    echo "Error: Could not resolve container ID for service '$GITLAB_SERVER_CONTAINER'."
    exit 1
fi

# Inspect network
NETWORK_NAME=$(docker inspect $GITLAB_SERVER_CONTAINER_ID --format '{{range $k, $v := .NetworkSettings.Networks}}{{$k}}{{end}}')

if [ -z "$NETWORK_NAME" ]; then
    echo "Warning: Could not detect network name. Defaulting to 'gitlab-net'."
    NETWORK_NAME="gitlab-net"
else
    echo "   Detected network: $NETWORK_NAME"
fi

# 3. Register Runner
echo "3. Registering Runner..."
docker compose exec $GITLAB_RUNNER_CONTAINER gitlab-runner register \
  --non-interactive \
  --url "http://$GITLAB_SERVER_CONTAINER" \
  --token "$RUNNER_TOKEN" \
  --executor "$RUNNER_EXECUTOR" \
  --docker-image "$DOCKER_IMAGE" \
  --docker-network-mode "$NETWORK_NAME" \
  --clone-url "http://$GITLAB_SERVER_CONTAINER" \
  --docker-volumes "/var/run/docker.sock:/var/run/docker.sock"

if [ $? -eq 0 ]; then
    echo "=== Registration Completed Successfully ==="
else
    echo "Error: Registration failed."
    exit 1
fi
