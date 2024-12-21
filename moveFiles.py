import os
import shutil
import sys
from datetime import datetime


todayDateDir = 'all_'+str(datetime.today()).split()[0]

def move_files_with_unique_names(src_dir):
    # Get the parent directory of the source directory
    parent_dir = os.path.dirname(src_dir)
    dst_dir = os.path.join(parent_dir, todayDateDir)  # 'all' will be created in the parent directory
    
    # Ensure the 'all' directory exists
    os.makedirs(dst_dir, exist_ok=True)
    exclude=[todayDateDir,]
    # Walk through the source directory
    for root, dirs, files in os.walk(src_dir,topdown=True):
        dirs[:] = [d for d in dirs if d not in exclude]
        for file in files:
            src_path = os.path.join(root, file)
            dst_path = os.path.join(dst_dir, file)

            # If the file already exists in the destination, add a suffix
            if os.path.exists(dst_path):
                base, ext = os.path.splitext(file)
                count = 1
                # Create a unique file name by adding a suffix (01, 02, etc.)
                while os.path.exists(dst_path):
                    new_name = f"{base}{count:02d}{ext}"
                    dst_path = os.path.join(dst_dir, new_name)
                    count += 1

            # Move the file to the destination
            shutil.move(src_path, dst_path)
            print(f"Moved: {src_path} -> {dst_path}")

# Check if the user provided the source directory as a command-line argument
if len(sys.argv) != 2:
    print("Usage: python move_files.py <src_dir>")
    sys.exit(1)

# Get the source directory from the command-line argument
src_dir = sys.argv[1]

# Check if the source directory exists
if not os.path.isdir(src_dir):
    print(f"Error: The source directory '{src_dir}' does not exist.")
    sys.exit(1)

# Call the function to move files
move_files_with_unique_names(src_dir)
