
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

# Fix Origin URL for Pushing (Access Token Support)
utils.update_origin_url()

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

def get_closed_mr_branches(open_branches):
    """
    Identifies shadow branches that exist but correspond to a branch that is no longer in the Open list.
    We check remote shadow branches 'origin/*_shadow' and see if the base branch is missing from 'open_branches' AND 'main'.
    """
    print("Checking for closed branches to finalize...")
    # Get all remote shadow branches
    output = utils.run_git(['branch', '-r'])
    shadow_branches = []
    for line in output.splitlines():
        line = line.strip()
        if '_shadow' in line and 'origin/' in line and not ('->' in line):
            branch = line.replace('origin/', '').replace('_shadow', '')
            shadow_branches.append(branch)
            
    closed_targets = []
    active_set = set(open_branches)
    active_set.add('main')
    
    for base_branch in shadow_branches:
        if base_branch not in active_set:
            # It exists as a shadow, but is not in Open MRs or Main.
            # It might be closed/merged.
            # We should check if the base branch still exists in Origin (Mirrored)?
            # If it exists, we update it one last time (maybe it was just merged and source branch pending deletion).
            # If it does NOT exist (source deleted), we can't update HEAD.
            # But the requirement is "Specially update HEAD".
            # If the source branch is gone, we can't get HEAD. 
            # We assume "Closed" means "Merged but branch ref might still exist" OR "We treat the last known state as final".
            # Let's check if 'origin/base_branch' exists.
            
            try:
                utils.run_git(['rev-parse', f'origin/{base_branch}'], check=False)
                # It exists! So we include it as a target.
                # The process_branch logic will check metadata. 
                # If metadata matches, it skips. 
                # BUT user said "Specially update HEAD". 
                # This implies even if it matches, maybe we force? 
                # Or maybe just ensuring it IS up to date is enough. 
                # "Previously it was open, now closed... update HEAD". 
                # If we just treat it as a target, standard logic ensures it matches HEAD.
                # If it matches HEAD, it is updated.
                print(f"Found closed/merged candidate: {base_branch}")
                closed_targets.append(base_branch)
            except Exception:
                print(f"Shadow exists for {base_branch} but source is gone. Skipping.")
    
    return closed_targets

STATE_FILE = "previous_open_branches.txt"
STATE_BRANCH = "sys/ci" # Branch to store the state file

def get_previous_open_branches(runner_cwd):
    """
    Reads the list of open branches from the previous run.
    Expects STATE_FILE to be in the current workspace (checked out sys/ci or similar).
    """
    # We need to fetch/checkout the state file from STATE_BRANCH
    try:
        utils.run_git(['fetch', 'origin', STATE_BRANCH], cwd=runner_cwd, check=False)
        content = utils.run_git(['show', f'origin/{STATE_BRANCH}:{STATE_FILE}'], cwd=runner_cwd, check=False)
        if content:
            return set(line.strip() for line in content.splitlines() if line.strip())
    except Exception:
        pass
    return set()

def save_current_open_branches(open_branches, runner_cwd):
    """
    Saves the current list of open branches to STATE_FILE on STATE_BRANCH.
    """
    print("Saving current Open MR list to state file...")
    state_ws = Path("state_workspace")
    if state_ws.exists(): shutil.rmtree(state_ws)
    
    try:
        repo_url = utils.get_authenticated_repo_url(runner_cwd)
        # Clone STATE_BRANCH
        utils.run_git(['clone', '--depth', '1', '-b', STATE_BRANCH, repo_url, str(state_ws)], cwd=".")
        
        # Write file
        (state_ws / STATE_FILE).write_text("\n".join(sorted(open_branches)))
        
        utils.configure_git_user()
        utils.run_git(['add', STATE_FILE], cwd=state_ws)
        
        # Commit & Push
        # Check if changed
        status = utils.run_git(['status', '--porcelain'], cwd=state_ws)
        if status:
            utils.run_git(['commit', '-m', 'Update previous_open_branches.txt [skip ci]'], cwd=state_ws)
            utils.push_changes(STATE_BRANCH, cwd=state_ws)
            print("State file updated.")
        else:
            print("State file unchanged.")
            
    except Exception as e:
        print(f"Failed to save state file: {e}")
    
    if state_ws.exists(): shutil.rmtree(state_ws)

def get_target_branches():
    runner_cwd = Path.cwd()

    # 1. Configured Targets
    targets_env = os.environ.get("TARGET_BRANCHES")
    manual_targets = [b.strip() for b in targets_env.split(",") if b.strip()] if targets_env else []
    
    # 2. Base Targets
    base_targets = {'main'}
    
    # 3. Current Open MRs
    current_open_mrs = set(get_open_mr_branches())
    
    # 4. Detect Closed Branches (Previously Open - Currently Open)
    previous_open_mrs = get_previous_open_branches(runner_cwd)
    
    # Identify branches that were open but are NOT open now
    newly_closed = previous_open_mrs - current_open_mrs
    
    # But we should exclude branches that are deleted? 
    # If a branch is closed AND deleted, we can't shadow it.
    # process_branch handles "clone failed" gracefully.
    
    print(f"Previous Open: {previous_open_mrs}")
    print(f"Current Open: {current_open_mrs}")
    print(f"Newly Closed Candidates: {newly_closed}")
    
    # Combine all targets
    all_targets = base_targets.union(manual_targets).union(current_open_mrs).union(newly_closed)
    
    # Save State for Next Run
    # The state should be the "Current Open MRs" (plus maybe manual?)
    # Strictly, "previous run's open branches" for next time is just current_open_mrs.
    save_current_open_branches(list(current_open_mrs), runner_cwd)
    
    sorted_targets = sorted(list(all_targets))
    print(f"Final Target Branches: {sorted_targets}")
    return sorted_targets

def check_remote_lock(shadow_branch, runner_cwd):
    try:
        utils.run_git(['fetch', 'origin', shadow_branch], cwd=runner_cwd, check=False)
        lock_content = utils.run_git(['show', f'origin/{shadow_branch}:{LOCK_FILE}'], cwd=runner_cwd, check=False)
        if lock_content:
            # User requested NOT to timeout, just respect existence.
            print(f"Branch {shadow_branch} is LOCKED. Skipping.")
            return True
        return False
    except Exception:
        return False

def push_lock_file(branch_shadow, runner_cwd):
    print(f"Acquiring lock for {branch_shadow}...")
    lock_ws = Path("lock_workspace")
    if lock_ws.exists(): shutil.rmtree(lock_ws)
    try:
        repo_url = utils.get_authenticated_repo_url(runner_cwd)
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
    repo_url = utils.get_authenticated_repo_url(runner_cwd)
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
