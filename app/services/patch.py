import os
import ast
from app.core.config import logger

def apply_local_patch(target_file: str, line_number: int, proposed_patch: str) -> bool:
    """
    Locally modifies the target file to insert the proposed patch at the specified line.
    Includes a safety validation check to guarantee the injected patch is valid Python syntax.
    """
    logger.info(f"[PATCH ENGINE] Attempting to patch {target_file} at line {line_number}...")
    
    # Absolute safety boundary check
    if not os.path.exists(target_file):
        logger.error(f"[PATCH ENGINE] Target file not found: {target_file}")
        return False

    try:
        # Read the original file data
        with open(target_file, "r") as f:
            lines = f.readlines()

        # Insert the patch code cleanly at the precise index line
        # Line numbers are 1-indexed, Python arrays are 0-indexed
        insert_idx = max(0, line_number - 1)
        lines.insert(insert_idx, f"{proposed_patch}\n")

        # Reconstruct file content
        updated_content = "".join(lines)

        # Pre-execution Syntax Integrity Check: Make sure the AI didn't output invalid code
        ast.parse(updated_content)

        # Write the clean verified patch back to the drive
        with open(target_file, "w") as f:
            f.write(updated_content)

        logger.info(f"[PATCH ENGINE] Successfully patched and validated syntax for {target_file}!")
        return True

    except SyntaxError as se:
        logger.error(f"[PATCH ENGINE] Syntax validation failed for proposed patch: {se}")
    except Exception as e:
        logger.error(f"[PATCH ENGINE] Runtime error during file overwrite: {e}")

    return False