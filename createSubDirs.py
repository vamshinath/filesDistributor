import os
import shutil
import sys

# Check if the script is being run with the correct number of arguments
if len(sys.argv) != 2:
    print("Usage: python split_files.py <source_directory>")
    sys.exit(1)

# Get the source directory from the command line argument
source_dir = sys.argv[1]

# Set the target directory to be the same as the source directory
target_dir = source_dir

# Number of files per subdirectory
files_per_subdir = 4000

# Check if the source directory exists
if not os.path.isdir(source_dir):
    print(f"Error: The directory {source_dir} does not exist.")
    sys.exit(1)

# List all files in the source directory
files = [f for f in os.listdir(source_dir) if os.path.isfile(os.path.join(source_dir, f))]

# Calculate how many subdirectories are needed
total_files = len(files)
num_subdirs = (total_files // files_per_subdir) + (1 if total_files % files_per_subdir > 0 else 0)

# Start distributing files into subdirectories
subdir_counter = 1
for i in range(0, total_files, files_per_subdir):
    # Create a new subdirectory
    subdir_name = os.path.join(target_dir, f"subdir_{subdir_counter}")
    os.makedirs(subdir_name, exist_ok=True)
    
    # Select the files for this subdirectory
    files_to_move = files[i:i + files_per_subdir]
    
    # Move each file to the new subdirectory
    for file in files_to_move:
        src_file = os.path.join(source_dir, file)
        dst_file = os.path.join(subdir_name, file)
        shutil.move(src_file, dst_file)
    
    print(f"Moved {len(files_to_move)} files to {subdir_name}")
    subdir_counter += 1

print("All files have been successfully moved into subdirectories.")
