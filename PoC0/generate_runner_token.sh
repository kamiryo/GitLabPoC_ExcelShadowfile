#!/bin/bash

# Configuration
GITLAB_SERVER_CONTAINER="gitlab-server"
RUBY_SCRIPT_LOCAL="gen_token.rb"
RUBY_SCRIPT_REMOTE="/tmp/gen_token.rb"

echo "Generating GitLab Runner token..."

# Create Ruby script locally ensuring Unix line endings (safe for WSL/Linux)
cat <<EOF > "$RUBY_SCRIPT_LOCAL"
r=Ci::Runner.new
r.runner_type='instance_type'
r.description='Docker-Runner-PoC'
r.tag_list=['docker', 'shadow-file']
r.run_untagged=true
r.locked=false
r.access_level='not_protected'
r.save!
print r.token
EOF

# Copy the script to the container
echo "Copying generation script to container..."
docker cp "$RUBY_SCRIPT_LOCAL" "$GITLAB_SERVER_CONTAINER:$RUBY_SCRIPT_REMOTE"

if [ $? -ne 0 ]; then
    echo "Error: Failed to copy script to container. Is gitlab-server running?"
    exit 1
fi

# Execute the script
echo "Executing token generation..."
RUNNER_TOKEN=$(docker exec "$GITLAB_SERVER_CONTAINER" gitlab-rails runner "$RUBY_SCRIPT_REMOTE" 2>/dev/null)

# Clean up remote script (optional)
docker exec "$GITLAB_SERVER_CONTAINER" rm "$RUBY_SCRIPT_REMOTE"

if [ -z "$RUNNER_TOKEN" ]; then
    echo "Error: Failed to generate token. Output is empty."
    exit 1
fi

# Trim any potential whitespace
RUNNER_TOKEN=$(echo "$RUNNER_TOKEN" | xargs)

echo "Token generated successfully: $RUNNER_TOKEN"

# Export for use in other scripts if sourced
export RUNNER_TOKEN
