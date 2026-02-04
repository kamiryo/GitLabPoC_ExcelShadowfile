import sys
import io

import os

import msoffcrypto
from pathlib import Path
from markitdown import MarkItDown


def load_passwords(password_file="passwords.txt"):
    """Load passwords from file in script dir or current dir."""
    candidates = []
    # Check script dir
    script_dir = Path(__file__).parent.parent # Assuming tools/script.py, so up one level usually? Or just script dir. 
    # Let's check: script is in tools/, passwords probably in root of PoC3.
    # But user might run from anywhere.
    # Let's try: 1. ENV VAR, 2. Current Dir, 3. Script Parent Dir
    
    search_paths = [
        Path.cwd() / password_file,
        Path(__file__).parent / password_file,
        Path(__file__).parent.parent / password_file
    ]
    
    for path in search_paths:
        if path.exists():
            print(f"Loading passwords from: {path}")
            try:
                with open(path, "r", encoding="utf-8") as f:
                    candidates = [line.strip() for line in f if line.strip()]
                break
            except Exception as e:
                print(f"Error reading {path}: {e}", file=sys.stderr)
                
    if not candidates:
        print("Warning: passwords.txt not found. Encrypted files will be skipped.", file=sys.stderr)
    return candidates

PASSWORDS = load_passwords()

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
