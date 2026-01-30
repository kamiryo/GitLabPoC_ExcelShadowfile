
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
    args.append(branch)
    run_git(args, cwd=cwd)
