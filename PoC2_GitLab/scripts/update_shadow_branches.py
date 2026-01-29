
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

def get_target_branches():
    targets_env = os.environ.get("TARGET_BRANCHES")
    if targets_env:
        return [b.strip() for b in targets_env.split(",") if b.strip()]
    print("WARNING: TARGET_BRANCHES not set. Defaulting to 'main'.")
    return ['main']

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
