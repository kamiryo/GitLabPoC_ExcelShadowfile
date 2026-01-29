import sys
import io
import os
import subprocess
import msoffcrypto
from pathlib import Path
from markitdown import MarkItDown

# List of passwords to try for encrypted files
# Load passwords from external file
try:
    with open(Path(__file__).parent / "passwords.txt", "r", encoding="utf-8") as f:
        PASSWORDS = [line.strip() for line in f if line.strip()]
except FileNotFoundError:
    print("Warning: passwords.txt not found. Using default empty list.", file=sys.stderr)
    PASSWORDS = []

def is_encrypted(file_path):
    """Check if the file is encrypted using msoffcrypto-tool."""
    try:
        with open(file_path, "rb") as f:
            file = msoffcrypto.OfficeFile(f)
            return True 
    except Exception:
        return False

def decrypt_file(file_path, password):
    """Attempt to decrypt the file with the given password. Returns bytes or None."""
    try:
        decrypted = io.BytesIO()
        with open(file_path, "rb") as f:
            file = msoffcrypto.OfficeFile(f)
            file.load_key(password=password)
            file.decrypt(decrypted)
        decrypted.seek(0)
        return decrypted
    except Exception:
        return None

def get_target_files(full_scan=False):
    """
    Returns a set of Path objects for logical file processing.
    If full_scan is True, returns all .xlsx/.xls files.
    Otherwise, attempts to find changed files via git.
    """
    target_extensions = {'.xlsx', '.xls'}
    files_to_process = set()
    current_dir = Path('.')

    # Check valid extensions
    def is_valid(p):
        return p.suffix.lower() in target_extensions and not p.name.startswith('~$') and p.is_file()

    if full_scan:
        print("Performing FULL SCAN...")
        for p in current_dir.rglob('*'):
            if is_valid(p):
                files_to_process.add(p)
        return files_to_process

    # Try incremental scan via git
    try:
        # Determine comparison range.
        # In GitLab CI, typically CI_COMMIT_BEFORE_SHA is available.
        # If not, use HEAD~1 if possible, or failback to full scan.
        before_sha = os.environ.get('CI_COMMIT_BEFORE_SHA')
        current_sha = os.environ.get('CI_COMMIT_SHA', 'HEAD')
        
        if not before_sha:
            # Fallback for local testing or initial commit
            before_sha = 'HEAD~1'
            print(f"CI_COMMIT_BEFORE_SHA not set, comparing {before_sha}..{current_sha}")

        # Get list of changed files
        cmd = ['git', 'diff', '--name-only', before_sha, current_sha]
        output = subprocess.check_output(cmd, stderr=subprocess.PIPE).decode('utf-8')
        
        changed_paths = output.strip().splitlines()
        print(f"Git determined {len(changed_paths)} changed files.")

        for p_str in changed_paths:
            p = Path(p_str)
            if p.exists() and is_valid(p):
                 files_to_process.add(p)
            elif not p.exists():
                print(f"Skipping deleted file: {p}")

    except Exception as e:
        print(f"Incremental scan failed ({e}). Fallback to FULL SCAN.", file=sys.stderr)
        return get_target_files(full_scan=True)

    return files_to_process

def main():
    """
    Main execution.
    usage: python generate_shadow.py [--all]
    """
    full_scan = '--all' in sys.argv
    
    targets = get_target_files(full_scan=full_scan)
    print(f"Target files to process: {len(targets)}")

    if not targets:
        print("No Excel files to update.")
        return

    md = MarkItDown()

    for excel_path in targets:
        try:
            print(f"Processing: {excel_path}")
            result = None
            
            # Primary attempt: Direct Conversion
            try:
                result = md.convert(str(excel_path))
            except Exception as e_convert:
                # Password check
                print(f"Direct conversion failed for {excel_path}: {e_convert}. Checking passwords...", file=sys.stderr)
                success = False
                for pwd in PASSWORDS:
                    try:
                        decrypted_stream = decrypt_file(excel_path, pwd)
                        if decrypted_stream:
                            temp_decrypted = excel_path.with_name(f".tmp_decrypted_{excel_path.name}")
                            with open(temp_decrypted, "wb") as tf:
                                tf.write(decrypted_stream.read())
                            try:
                                result = md.convert(str(temp_decrypted))
                                success = True
                                print(f"Decrypted with password: {pwd}")
                                temp_decrypted.unlink()
                                break
                            except:
                                temp_decrypted.unlink()
                    except:
                        continue
                if not success:
                    print(f"Failed to decrypt or convert {excel_path}.", file=sys.stderr)
                    continue

            if result:
                # Output: .<name>.<ext>.shadow
                output_name = f".{excel_path.name}.shadow"
                output_path = excel_path.parent / output_name
                output_path.write_text(result.text_content, encoding='utf-8')
                print(f"Generated: {output_path}")

        except Exception as e:
            print(f"Error processing {excel_path}: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()
