from pathlib import Path
from tabulate import tabulate
import os,sys
import glob


def count_files_by_actor(base_dir):
    # Dictionary to store file counts
    file_counts = {}
    
    # Use pathlib to iterate through directories and count files
    base_path = Path(base_dir)
    for actor_dir in base_path.iterdir():
        if actor_dir.is_dir():
            # Count all files in the actor's directory
            actor_dirt = Path(actor_dir,'toTrain')
            file_count = len(list(actor_dirt.glob("*")))
            file_counts[actor_dir.name] = file_count

    return file_counts

# Replace '/path/to/actors/images' with the path to your actors' directories
base_directory = os.path.abspath(sys.argv[1])
file_counts = count_files_by_actor(base_directory)

# Sort file counts by count (descending order)
sorted_counts = sorted(file_counts.items(), key=lambda x: x[1], reverse=True)

# Format results as a table
table = [["Actor", "File Count"]] + sorted_counts
print(tabulate(table, headers="firstrow", tablefmt="grid"))
