import sys
import io

import os

import msoffcrypto
from pathlib import Path
from markitdown import MarkItDown


from dotenv import load_dotenv, find_dotenv

# Load environment variables from .env file
# Priority 1: .env in the same directory as this script
script_env = Path(__file__).parent / ".env"
if script_env.exists():
    load_dotenv(script_env)

# Priority 2: Standard search from CWD up
load_dotenv(find_dotenv())

def load_passwords():
    """Load passwords from SHADOW_PASSWORDS env var (comma separated)."""
    raw = os.environ.get("SHADOW_PASSWORDS", "")
    if not raw:
        return []
    return [p.strip() for p in raw.split(",") if p.strip()]

PASSWORDS = load_passwords()

def decrypt_file(file_path, password):
    """
    Attempt to decrypt an Office file with a password.
    Returns: A file-like object (io.BytesIO) of the decrypted content, or None on failure.
    """
    try:
        decrypted = io.BytesIO()
        with open(file_path, "rb") as f:
            office_file = msoffcrypto.OfficeFile(f)
            office_file.load_key(password=password)
            office_file.decrypt(decrypted)
        decrypted.seek(0)
        return decrypted
    except Exception:
        # Decryption failed (wrong password or not encrypted)
        return None

def get_target_files(root_dir="doc"):
    """
    Recursively scans root_dir for Excel files.
    """
    root_path = Path(root_dir)
    if not root_path.exists():
        print(f"Directory not found: {root_path}", file=sys.stderr)
        return set()

    target_extensions = {'.xlsx', '.xls'}
    files_to_process = set()
    
    print(f"Scanning directory: {root_path.resolve()}")

    for p in root_path.rglob('*'):
        if p.is_file() and p.suffix.lower() in target_extensions and not p.name.startswith('~$'):
            files_to_process.add(p)
            
    return files_to_process

def main():
    """
    Main execution.
    usage: python generate_shadow_recursive.py [target_directory]
    """
    target_dir = "doc"
    if len(sys.argv) > 1:
        target_dir = sys.argv[1]
    
    targets = get_target_files(target_dir)
    print(f"Found {len(targets)} Excel files in '{target_dir}'.")

    if not targets:
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
                print(f"  [Debug] Direct conversion failed: {e_convert}", file=sys.stderr)
                # print(f"Direct conversion failed for {excel_path}. Checking passwords...", file=sys.stderr)
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
                                print(f"  Decrypted with password: {pwd}")
                                temp_decrypted.unlink()
                                break
                            except:
                                if temp_decrypted.exists(): temp_decrypted.unlink()
                    except:
                        continue
                if not success:
                    print(f"  Failed to convert (Encrypted?): {excel_path.name}", file=sys.stderr)
                    continue

            if result:
                # Output: .<name>.<ext>.shadow
                output_name = f".{excel_path.name}.shadow"
                output_path = excel_path.parent / output_name
                output_path.write_text(result.text_content, encoding='utf-8')
                print(f"  Generated Shadow: {output_path.name}")

        except Exception as e:
            print(f"Error processing {excel_path}: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()
