
import os
import sys
import utils

# Configuration
SOURCE_REPO_URL = os.environ.get("SOURCE_REPO_URL")

def mirror_repository():
    if not SOURCE_REPO_URL:
        print("Error: SOURCE_REPO_URL env var not set.")
        sys.exit(1)

    print(f"--- Starting Mirroring from {SOURCE_REPO_URL} ---")
    
    # Fix Origin URL for Pushing (Access Token Support)
    utils.update_origin_url()

    # Strategy:
    # 1. Fetch all branches from Source
    # 2. Push them to Origin (Shadow Repo), pruning deleted ones
    # 3. BUT protect 'sys/ci' and '*_shadow' from being pruned/overwritten

    # We assume we are in a git repo (the Runner's checkout of Shadow Repo).
    # But for a clean mirror, we might want to operate in a temp clone or properly configured workspace.
    # However, to Push to Origin, we need credentials. The Runner has them for the current repo.
    
    # Add Source Remote
    try:
        utils.run_git(['remote', 'add', 'source_repo', SOURCE_REPO_URL], check=False)
    except Exception:
        pass # Already exists?

    # Fetch Source
    print("Fetching from source_repo...")
    utils.run_git(['fetch', 'source_repo'])

    # Get list of source branches
    # We want to mirror source_repo/* to origin/*
    # Excluding 'sys/ci' and others if they exist in source (unlikely but safe to exclude)
    
    # A simple 'git push --mirror' is dangerous because it wipes local-only branches like sys/ci.
    # We must push specific refs.
    
    # Get all remote branches from source_repo
    output = utils.run_git(['branch', '-r'])
    source_branches = []
    for line in output.splitlines():
        line = line.strip()
        if line.startswith('source_repo/') and not ('->' in line):
            branch = line.replace('source_repo/', '')
            source_branches.append(branch)
    
    print(f"Found source branches: {source_branches}")
    
    for branch in source_branches:
        # Safety check: Don't mirror if it conflicts with our infrastructure branches
        if branch == 'sys/ci' or branch.endswith('_shadow'):
            print(f"Skipping protected/reserved branch name: {branch}")
            continue
            
        print(f"Syncing {branch}...")
        # Force push source ref to origin ref
        # This makes Shadow Repo's 'branch' identical to Design Repo's 'branch'
        refspec = f"refs/remotes/source_repo/{branch}:refs/heads/{branch}"
        try:
            utils.run_git(['push', 'origin', refspec, '--force'], check=False)
        except Exception as e:
            print(f"Failed to sync {branch}: {e}")

    # TODO: Pruning logic (delete branches on Origin that no longer exist on Source)
    # This requires listing Origin branches, diffing with Source branches, and deleting leftovers.
    # For PoC, we can skip strict pruning or implement it carefully.
    # Ideally, we only prune branches that are NOT 'sys/ci' and NOT '*_shadow'.

if __name__ == "__main__":
    mirror_repository()
