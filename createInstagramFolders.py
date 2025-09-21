import os
import re
import sys
import datetime
import shutil

def is_valid_unix_timestamp(ts_string):
    try:
        ts_int = int(ts_string)
        min_ts = 0
        max_ts = 2147483647
        if len(ts_string) == 10 and min_ts <= ts_int <= max_ts:
            datetime.datetime.fromtimestamp(ts_int)
            return True
        return False
    except Exception:
        return False

def create_folder_and_move_files(root_dir):
    pattern = re.compile(r'(\d{10})')
    moved_count = 0
    failed_count = 0

    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            match = pattern.search(filename)
            if match and is_valid_unix_timestamp(match.group(1)):
                timestamp_index = match.start(1)
                folder_name = filename[:timestamp_index].rstrip('_')
                src_path = os.path.join(dirpath, filename)
                dest_folder = os.path.join(root_dir, folder_name)
                os.makedirs(dest_folder, exist_ok=True)
                dest_path = os.path.join(dest_folder, filename)
                try:
                    shutil.move(src_path, dest_path)
                    print(f"[Moved] {src_path} -> {dest_path}")
                    moved_count += 1
                except Exception as e:
                    print(f"[Error] Failed to move {src_path}: {e}")
                    failed_count += 1

    print(f"Move completed. Files moved successfully: {moved_count}, Failures: {failed_count}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <directory_to_scan>")
        sys.exit(1)
    root_directory = sys.argv[1]
    if not os.path.isdir(root_directory):
        print(f"Directory does not exist: {root_directory}")
        sys.exit(1)

    create_folder_and_move_files(root_directory)

