import os
import re
import shutil
import datetime
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

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

def move_file(task):
    src_path, dest_dir, filename = task
    try:
        dest_path = os.path.join(dest_dir, filename)
        shutil.move(src_path, dest_path)
        print(f"[Moved] {src_path} -> {dest_path}")
        return True
    except Exception as e:
        print(f"[Error] Failed to move {src_path}: {e}")
        return False

def move_tasks_multithreaded(tasks, num_workers):
    moved_count = 0
    failed_count = 0
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = [executor.submit(move_file, task) for task in tasks]
        for future in as_completed(futures):
            if future.result():
                moved_count += 1
            else:
                failed_count += 1
    return moved_count, failed_count

def scan_and_move(root_dir, dest_dir, batch_size=1000):
    pattern = re.compile(r'(\d{10})')
    tasks = []
    total_moved = 0
    total_failed = 0

    print(f"Scanning directory: {root_dir}")
    num_workers = min(32, os.cpu_count() * 2)
    print("wokers:", num_workers)
    for dirpath, _, filenames in os.walk(root_dir):
        if os.path.abspath(dirpath) == os.path.abspath(dest_dir):
            continue
        for filename in filenames:
            match = pattern.search(filename)
            if match and is_valid_unix_timestamp(match.group(1)):
                src_path = os.path.join(dirpath, filename)
                tasks.append((src_path, dest_dir, filename))

                if len(tasks) >= batch_size:
                    print(f"Processing batch of {len(tasks)} files...")
                    moved, failed = move_tasks_multithreaded(tasks, num_workers)
                    total_moved += moved
                    total_failed += failed
                    tasks = []

        # After finishing a directory, move any remaining tasks
        if tasks:
            print(f"Processing remaining batch of {len(tasks)} files in directory {dirpath}...")
            moved, failed = move_tasks_multithreaded(tasks, num_workers)
            total_moved += moved
            total_failed += failed
            tasks = []

    print(f"Scan and move completed. Total moved: {total_moved}, Total failed: {total_failed}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <directory_to_scan>")
        sys.exit(1)
    root_directory = sys.argv[1]
    if not os.path.isdir(root_directory):
        print(f"Directory does not exist: {root_directory}")
        sys.exit(1)
    destination_directory = os.path.join(root_directory, "InstagramDownloads")
    os.makedirs(destination_directory, exist_ok=True)
    print(f"Destination directory set to: {destination_directory}")

    scan_and_move(root_directory, destination_directory)
