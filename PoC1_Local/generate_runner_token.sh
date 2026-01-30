#!/bin/bash

# Execute gitlab-rails runner command inside the container to create a new runner and get the token
# This script creates a runner with the following attributes:
#   runner_type: instance_type
#   description: Docker-Runner-PoC
#   tag_list: ['docker', 'shadow-file']
#   run_untagged: true
#   locked: false
#   access_level: not_protected

echo "Generating GitLab Runner token..."

# The Ruby script is passed as a one-liner to gitlab-rails runner
RUBY_SCRIPT="r=Ci::Runner.new;r.runner_type='instance_type';r.description='Docker-Runner-PoC';r.tag_list=['docker','shadow-file'];r.run_untagged=true;r.locked=false;r.access_level='not_protected';r.save!;print r.token"

RUNNER_TOKEN=$(docker exec gitlab-server gitlab-rails runner "$RUBY_SCRIPT" 2>/dev/null)

# Clean up any potential garbage output (though print should be clean, rails runner explicitly can output warnings)
# Taking the last line might be safer if there are warnings, but print r.token is usually direct. 
# However, docker exec might output tty info if -it is used (we avoided -it here).
# We also redirected stderr to /dev/null to keep it clean.

if [ -z "$RUNNER_TOKEN" ]; then
    echo "Failed to generate token. Ensure gitlab-server is running and ready."
    exit 1
fi

echo "Token generated successfully: $RUNNER_TOKEN"

# For use in subsequent shell commands (if sourced)
export RUNNER_TOKEN
