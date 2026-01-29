
import os
import sys
import json
import shutil
import time
from pathlib import Path
import utils
import generate_shadow

# Configuration
# Note: We rely on the local repository state (which has been mirrored by the previous step)
# OR we can still clone fresh. 
# Since we decoupled, this script assumes "Origin" has the latest code (from mirror step).
# So we can just clone from Origin (Shadow Repo).

SHADOW_REPO_DIR = Path("shadow_workspace")
SHADOW_METADATA_FILE = "shadow_metadata.json"
LOCK_FILE = "shadow_lock.lock"
LOCK_TIMEOUT_SECONDS = 600

import requests

def get_open_mr_branches():
    """
    Fetches source branches of OPEN Merge Requests from GitLab API.
    Requires SOURCE_PROJECT_ID and ACCESS_TOKEN.
    """
    project_id = os.environ.get("SOURCE_PROJECT_ID")
    token = os.environ.get("ACCESS_TOKEN")
    api_url = os.environ.get("CI_API_V4_URL", "https://gitlab.com/api/v4")
    
    if not project_id or not token:
        print("WARNING: SOURCE_PROJECT_ID or ACCESS_TOKEN not set. Cannot fetch MRs via API.")
        return []

    print(f"Fetching Open MRs for Project ID {project_id}...")
    headers = {"PRIVATE-TOKEN": token}
    branches = set()
    
    try:
        # Pagination handling could be added, but for PoC we fetch page 1 (default 20->100 generally sufficient or need per_page)
        resp = requests.get(f"{api_url}/projects/{project_id}/merge_requests?state=opened&per_page=100", headers=headers)
        if resp.status_code == 200:
            mrs = resp.json()
            for mr in mrs:
                source_branch = mr.get("source_branch")
                if source_branch:
                    branches.add(source_branch)
            print(f"Found {len(branches)} branches from Open MRs.")
        else:
            print(f"Failed to fetch MRs: {resp.status_code} {resp.text}")
    except Exception as e:
        print(f"API Request failed: {e}")
        
    return list(branches)

def get_target_branches():
    # 1. Configured Targets (Env Var)
    targets_env = os.environ.get("TARGET_BRANCHES")
    manual_targets = [b.strip() for b in targets_env.split(",") if b.strip()] if targets_env else []
    
    # 2. Always include 'main' (unless explicitly excluded? No, usually required)
    base_targets = {'main'}
    
    # 3. Open MRs (Auto-detection)
    mr_targets = get_open_mr_branches()
    
    # Combine
    all_targets = base_targets.union(manual_targets).union(mr_targets)
    
    # Filter: Only branches that actually exist in our local mirror (Origin)
    # This prevents trying to shadow a branch that hasn't been mirrored yet or doesn't exist.
    # But checking remote branches is expensive? No, we can list them.
    # For PoC, let's just return the list. `process_branch` handles missing branches gracefully.
    
    sorted_targets = sorted(list(all_targets))
    print(f"Final Target Branches: {sorted_targets}")
    return sorted_targets

def check_remote_lock(shadow_branch, runner_cwd):
    try:
        utils.run_git(['fetch', 'origin', shadow_branch], cwd=runner_cwd, check=False)
        lock_content = utils.run_git(['show', f'origin/{shadow_branch}:{LOCK_FILE}'], cwd=runner_cwd)
        if not lock_content: return False
        lock_time = float(lock_content.strip())
        if time.time() - lock_time > LOCK_TIMEOUT_SECONDS: return False
        return True
    except Exception:
        return False

def push_lock_file(branch_shadow, runner_cwd):
    print(f"Acquiring lock for {branch_shadow}...")
    lock_ws = Path("lock_workspace")
    if lock_ws.exists(): shutil.rmtree(lock_ws)
    try:
        repo_url = utils.run_git(['config', '--get', 'remote.origin.url'], cwd=runner_cwd)
        utils.run_git(['clone', '--depth', '1', '-b', branch_shadow, repo_url, str(lock_ws)], cwd=".")
    except:
        lock_ws.mkdir()
        utils.run_git(['init'], cwd=lock_ws)
        utils.run_git(['checkout', '-b', branch_shadow], cwd=lock_ws)
    
    (lock_ws / LOCK_FILE).write_text(str(time.time()))
    utils.configure_git_user()
    utils.run_git(['add', LOCK_FILE], cwd=lock_ws)
    utils.run_git(['commit', '-m', 'Acquire Lock [skip ci]'], cwd=lock_ws, check=False)
    try:
        utils.push_changes(branch_shadow, cwd=lock_ws)
    except:
        pass
    if lock_ws.exists(): shutil.rmtree(lock_ws)

def process_branch(branch_name):
    # This script assumes 'origin' (Shadow Repo) already has the latest copy of 'branch_name'
    # because mirror_design_repo.py ran before this.
    
    print(f"--- Processing Shadow for: {branch_name} ---")
    shadow_branch_name = f"{branch_name}_shadow"
    runner_cwd = Path.cwd()

    if check_remote_lock(shadow_branch_name, runner_cwd):
        print("Locked. Skipping.")
        return
    
    push_lock_file(shadow_branch_name, runner_cwd)

    # Clone the Branch from Origin (which is now mirrored)
    workspace = SHADOW_REPO_DIR
    if workspace.exists(): shutil.rmtree(workspace)
    
    # We clone from CURRENT REPO (Origin)
    repo_url = utils.run_git(['config', '--get', 'remote.origin.url'], cwd=runner_cwd)
    try:
        utils.run_git(['clone', '--depth', '1', '-b', branch_name, repo_url, str(workspace)])
    except Exception as e:
        print(f"Branch {branch_name} not found in Shadow Repo (Mirroring failed?): {e}")
        return

    source_sha = utils.run_git(['rev-parse', 'HEAD'], cwd=workspace)
    
    # Check Metadata
    try:
        metadata_content = utils.run_git(['show', f'origin/{shadow_branch_name}:{SHADOW_METADATA_FILE}'], cwd=runner_cwd)
        data = json.loads(metadata_content)
        if data.get("source_sha") == source_sha:
            print(f"Skipping {branch_name}: Already up to date.")
            return
    except:
        pass

    # Generate
    print("Generating shadows...")
    generate_shadow.process_directory(workspace, recursive=True)
    
    # Commit & Push
    utils.configure_git_user()
    metadata = {"source_sha": source_sha, "updated_at": time.time(), "source_branch": branch_name}
    (workspace / SHADOW_METADATA_FILE).write_text(json.dumps(metadata, indent=2))
    
    utils.run_git(['add', '.'], cwd=workspace)
    utils.run_git(['commit', '-m', f'Shadow update for {branch_name} ({source_sha})'], cwd=workspace, check=False)
    
    # We push back to Origin
    utils.push_changes(shadow_branch_name, cwd=workspace, force=True)
    print(f"Completed {branch_name}.")

if __name__ == "__main__":
    targets = get_target_branches()
    for branch in targets:
        process_branch(branch)
