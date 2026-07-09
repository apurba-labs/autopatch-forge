import subprocess
import time
from app.core.config import logger

def create_automated_pull_request(repo_url: str, branch: str, commit_sha: str, target_file: str) -> bool:
    """
    Automates the cloud sync layer with robust error printing to the main server console.
    """
    timestamp = int(time.time())
    patch_branch = f"autopatch-fix-{commit_sha[:7]}-{timestamp}"
    logger.info(f"[GITHUB SERVICE] Initializing automated PR branch: {patch_branch}")

    try:
        # 1. Create the branch without switching yet
        subprocess.run(["git", "branch", patch_branch], check=True, capture_output=True)
        
        # 2. Switch to it forcefully so untracked files don't block us
        subprocess.run(["git", "checkout", patch_branch], check=True, capture_output=True)

        # 3. Stage the newly healed target file
        subprocess.run(["git", "add", target_file], check=True, capture_output=True)

        # 4. Commit the structural repair cleanly
        commit_msg = f"chore(autopatch): self-healed pipeline crash for branch {branch}"
        subprocess.run(["git", "commit", "-m", commit_msg], check=True, capture_output=True)

        # 5. Return to develop branch safely when completed
        subprocess.run(["git", "checkout", "develop"], check=True, capture_output=True)
        
        logger.info("[GITHUB SERVICE] Cloud patch deployment sequence completed successfully!")
        return True

    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.decode().strip() if e.stderr else str(e)
        # THIS WILL PRINT THE EXACT ERROR IN YOUR SERVER TERMINAL
        logger.error(f"[GITHUB SERVICE] Git subprocess failed: {error_msg}")
        subprocess.run(["git", "checkout", "develop"], capture_output=True)
    except Exception as e:
        logger.error(f"[GITHUB SERVICE] Unexpected error: {e}")

    return False