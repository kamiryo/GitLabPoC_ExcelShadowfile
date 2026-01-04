#!/bin/bash

# Function to check if GitLab is ready
check_gitlab_ready() {
    # Check for HTTP 200 response
    if curl -s -o /dev/null -w "%{http_code}" http://localhost | grep -qE "200|301|302"; then
        return 0
    fi
    return 1
}

# Start services
echo "Starting GitLab services..."
docker compose up -d

echo "Waiting for GitLab to become ready (this may take 10+ minutes)..."
start_time=$(date +%s)
timeout=900 # 15 minutes

while true; do
    current_time=$(date +%s)
    elapsed=$((current_time - start_time))

    if [ $elapsed -gt $timeout ]; then
        echo "Timeout reached. GitLab did not become ready in time."
        docker compose logs --tail=20 gitlab-server
        exit 1
    fi

    if check_gitlab_ready; then
        echo "GitLab is ready! (HTTP 200 received)"
        exit 0
    fi

    echo "Waiting... ($elapsed seconds elapsed)"
    sleep 30
done
