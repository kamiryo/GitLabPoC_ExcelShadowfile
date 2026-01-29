
import sys
import io
import os
import msoffcrypto
from pathlib import Path
from markitdown import MarkItDown

def load_passwords(password_file="passwords.txt"):
    try:
        # Resolves relative to this script
        base_path = Path(__file__).parent
        path = base_path / password_file
        if not path.exists():
            # Fallback check in parent or current dir
            if (Path.cwd() / password_file).exists():
                path = Path.cwd() / password_file
        
        with open(path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except Exception:
        print("Warning: passwords.txt not found. Using default empty list.", file=sys.stderr)
        return []

def decrypt_file(file_path, password):
    """Attempt to decrypt the file with the given password."""
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

def generate_shadow_for_file(excel_path, passwords=None, force=False):
    """
    Generates a shadow file for a single Excel file.
    Returns the path to the generated shadow file if successful, otherwise None.
    """
    if passwords is None:
        passwords = []
    
    excel_path = Path(excel_path)
    if not excel_path.exists():
        print(f"File not found: {excel_path}", file=sys.stderr)
        return None

    md = MarkItDown()
    result = None

    try:
        # Primary attempt: Direct Conversion
        try:
            result = md.convert(str(excel_path))
        except Exception:
            # Encrypted? Try passwords
            success = False
            for pwd in passwords:
                decrypted_stream = decrypt_file(excel_path, pwd)
                if decrypted_stream:
                    # MarkItDown needs a file path usually, or maybe it can take stream? 
                    # The library seems completely file-path based in previous code.
                    # Workaround: Create temp file
                    temp_decrypted = excel_path.with_name(f".tmp_decrypted_{excel_path.name}")
                    try:
                        with open(temp_decrypted, "wb") as tf:
                            tf.write(decrypted_stream.read())
                        
                        result = md.convert(str(temp_decrypted))
                        success = True
                        print(f"Decrypted '{excel_path.name}' with password.", file=sys.stderr)
                        temp_decrypted.unlink()
                        break
                    except Exception as e:
                        print(f"Conversion failed after decryption: {e}", file=sys.stderr)
                        if temp_decrypted.exists():
                            temp_decrypted.unlink()
            
            if not success and not result:
                print(f"Failed to convert {excel_path} (Encryption or Format Error).", file=sys.stderr)
                return None

        if result:
            # Output: .<name>.<ext>.shadow
            # Example: data.xlsx -> .data.xlsx.shadow
            output_name = f".{excel_path.name}.shadow"
            output_path = excel_path.parent / output_name
            # Ensure parent exists (should, since input exists)
            output_path.write_text(result.text_content, encoding='utf-8')
            print(f"Generated: {output_path}")
            return output_path

    except Exception as e:
        print(f"Critical error processing {excel_path}: {e}", file=sys.stderr)
        return None

def process_directory(directory=".", recursive=True, passwords=None):
    """
    Scans directory for Excel files and generates shadows.
    """
    if passwords is None:
        passwords = load_passwords()
        
    target_extensions = {'.xlsx', '.xls'}
    directory = Path(directory)
    
    pattern = "**/*" if recursive else "*"
    
    count = 0
    for p in directory.glob(pattern):
        if p.is_file() and p.suffix.lower() in target_extensions and not p.name.startswith('~$'):
            ret = generate_shadow_for_file(p, passwords)
            if ret:
                count += 1
    return count

if __name__ == "__main__":
    # If run directly, perform full scan of current directory
    process_directory()
