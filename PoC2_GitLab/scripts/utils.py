
import subprocess
import os
import sys
import shutil
from pathlib import Path

def run_git(args, cwd=None, check=True):
    """Run a git command."""
    cmd = ['git'] + args
    print(f"DEBUG: Running git {' '.join(args)}")
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"Error running git command: {cmd}\nStderr: {result.stderr}", file=sys.stderr)
        raise subprocess.CalledProcessError(result.returncode, cmd, result.stdout, result.stderr)
    return result.stdout.strip()

def get_current_sha(cwd=None):
    return run_git(['rev-parse', 'HEAD'], cwd=cwd)

def fetch_origin(cwd=None):
    run_git(['fetch', 'origin'], cwd=cwd)

def get_remote_branches(cwd=None):
    output = run_git(['branch', '-r'], cwd=cwd)
    branches = []
    for line in output.splitlines():
        line = line.strip()
        if '->' in line: continue
        if line.startswith('origin/'):
            branches.append(line.replace('origin/', ''))
    return branches

def configure_git_user(email="shadow-bot@example.com", name="Shadow Bot"):
    run_git(['config', '--global', 'user.email', email], check=False)
    run_git(['config', '--global', 'user.name', name], check=False)

def clone_repo(url, dest, depth=1):
    if Path(dest).exists():
        shutil.rmtree(dest)
    run_git(['clone', '--depth', str(depth), url, dest], cwd=".")

def push_changes(branch_name, cwd=None, force=False):
    args = ['push', 'origin', f'HEAD:{branch_name}']
    if force:
        args.append('--force')
    run_git(args, cwd=cwd)

def checkout_branch(branch, cwd=None, create=False):
    args = ['checkout']
    if create:
        args.append('-b')

def get_authenticated_repo_url(cwd=None):
    """
    Returns the repository URL with:
    1. 'localhost' replaced by 'gitlab-server' (for Docker networking).
    2. ACCESS_TOKEN injected if available (for Push permissions).
    """
    token = os.environ.get("ACCESS_TOKEN")
    ci_url = os.environ.get("CI_REPOSITORY_URL")
    
    url = ci_url
    if not url:
        # Fallback to current config
        try:
            url = run_git(['config', '--get', 'remote.origin.url'], cwd=cwd)
        except:
            pass
            
    if not url:
        return None

    # Fix localhost -> gitlab-server
    url = url.replace("localhost", "gitlab-server")
    
    # Inject Access Token if available
    if token:
        # Format: https://gitlab-ci-token:TOKEN@host/path.git
        # We want: http://oauth2:ACCESS_TOKEN@host/path.git
        if "@" in url:
            # Strip existing auth
            protocol, rest = url.split("://", 1)
            host_path = rest.split("@", 1)[-1]
            url = f"{protocol}://oauth2:{token}@{host_path}"
        else:
            # Just insert
            protocol, rest = url.split("://", 1)
            url = f"{protocol}://oauth2:{token}@{rest}"
            
    return url

def update_origin_url(cwd=None):
    """Updates the 'origin' remote to use the authenticated URL (for Pushing)."""
    url = get_authenticated_repo_url(cwd)
    if url:
        print(f"DEBUG: Updating origin to authenticated URL...")
        # Don't print the actual URL to avoid leaking tokens in logs
        run_git(['remote', 'set-url', 'origin', url], cwd=cwd, check=False)
