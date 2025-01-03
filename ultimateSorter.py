import os
import shutil,sys
from pathlib import Path

# Define the size categories
size_categories = [
    (50 * 1024, '1_1KB_50KB'),
    (100 * 1024, '2_51KB_100KB'),
    (300 * 1024, '3_101KB_300KB'),
    (1 * 1024 * 1024, '4_301KB_1MB'),
    (5 * 1024 * 1024, '5_1MB_5MB'),
    (10 * 1024 * 1024, '6_5MB_10MB'),
    (50 * 1024 * 1024, '7_10MB_50MB'),
    (200 * 1024 * 1024, '8_50MB_200MB'),
    (600 * 1024 * 1024, '9_200MB_600MB'),
    (1 * 1024 * 1024 * 1024, '10_600MB_1GB'),
    (5 * 1024 * 1024 * 1024, '11_1GB_5GB'),
    (10 * 1024 * 1024 * 1024, '12_5GB_10GB'),
    (20 * 1024 * 1024 * 1024, '13_10GB_20GB')
]

# Common file type groups
extension_categories = {
    'images': {'jpg', 'jpeg', 'avif', 'webp', 'png', 'gif', 'bmp', 'tiff', 'heif', 'raw', 'ico', 'svg', 'ppm', 'pbm', 'pgm'},
    'videos': {'mp4', 'avi', 'mov', 'mkv', 'flv', 'webm', 'wmv', 'mpeg', 'mpg', '3gp', 'ogv', 'm4v', 'hevc', 'h264', 'h265', 'vp8', 'vp9', 'f4v', 'rm', 'ram', 'asf', 'divx'},
    'audios': {'mp3', 'aac', 'ogg', 'wma', 'flac', 'm4a', 'opus', 'wav', 'aiff', 'pcm', 'alac', 'au', 'ra', 'ape', 'spx', 'dts'},
    'documents': {'txt', 'rtf', 'md', 'log', 'csv', 'tsv', 'doc', 'docx', 'odt', 'pages', 'xls', 'xlsx', 'ppt', 'pptx', 'pdf', 'tex', 'bib', 'sty', 'epub', 'mobi', 'azw3'},
    'archives': {'zip', 'tar', 'gz', 'rar', '7z', 'tar.gz', 'tar.bz2', 'xz', 'cab', 'iso', 'lzma', 'tar.xz', 'tar.lz'},
    'executables': {'exe', 'bat', 'msi', 'com', 'vbs', 'sh', 'bin', 'out', 'app', 'dmg', 'pkg'},
    'webfiles': {'html', 'htm', 'css', 'js', 'jsx', 'ts', 'tsx', 'json', 'php', 'py', 'rb', 'pl', 'jsp', 'asp', 'cfm', 'xml', 'yml', 'xsl', 'yaml'},
    'databases': {'sql', 'db', 'sqlite', 'mdb', 'accdb', 'json', 'bson', 'couchdb'},
    'fonts': {'ttf', 'otf', 'woff', 'woff2', 'fnt', 'bdf'},
    'configs': {'conf', 'ini', 'cfg', 'settings', 'properties'},
    'backups': {'bak', 'old', 'swp', '~', 'bk', 'backup'},
    'cad': {'dwg', 'dxf', 'step', 'iges', 'stl', 'gcode', 'skp', 'obj', 'fbx', 'dae', 'blend', '3ds', 'x3d'},
}


# Function to classify and organize files based on size and type
def organize_files_by_size_and_type(base_dir):
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            file_path = os.path.join(root, file)
            if os.path.isfile(file_path):
                file_size = os.path.getsize(file_path)
                
                # Determine the category based on size
                target_dir = None
                for size_limit, category in size_categories:
                    if file_size <= size_limit:
                        target_dir = category
                        break
                if target_dir:
                    # Create the target directory if it doesn't exist
                    target_dir_path = Path(base_dir) / target_dir
                    target_dir_path.mkdir(parents=True, exist_ok=True)
                    
                    # Get the file extension and normalize it
                    ext = file.split('.')[-1].lower()
                    
                    file_category = 'others'  # Default category
                    for category, extensions in extension_categories.items():
                        if ext in extensions:
                            file_category = category
                            break


                    # Create the file type directory
                    file_type_dir = target_dir_path / file_category
                    file_type_dir.mkdir(parents=True, exist_ok=True)
                    
                    # Count files already present in the file type directory
                    existing_files = list(file_type_dir.rglob('*'))
                    file_count = len(existing_files)
                    
                    # Determine which subdirectory (dir0, dir1, etc.) the file should go to
                    dir_number = file_count // 1000  # Floor division to get the correct directory number
                    
                    # Only create a new subdirectory if dir_number > 0
                    subdir_name = f"dir{dir_number}"
                    subdir = file_type_dir / subdir_name
                    
                    subdir.mkdir(parents=True, exist_ok=True)

                    # Move the file to the appropriate subdirectory
                    shutil.move(file_path, subdir / file)

# Set the base directory where your files are located
base_directory = os.path.abspath(sys.argv[1])

# Organize the files
organize_files_by_size_and_type(base_directory)
