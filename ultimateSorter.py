import os
import shutil
import sys
from pathlib import Path
from collections import defaultdict
import hashlib

# --- Size Categories ---
size_categories = [
    (50 * 1024, "1_1KB_50KB"),
    (100 * 1024, "2_51KB_100KB"),
    (300 * 1024, "3_101KB_300KB"),
    (1 * 1024 * 1024, "4_301KB_1MB"),
    (5 * 1024 * 1024, "5_1MB_5MB"),
    (10 * 1024 * 1024, "6_5MB_10MB"),
    (50 * 1024 * 1024, "7_10MB_50MB"),
    (200 * 1024 * 1024, "8_50MB_200MB"),
    (600 * 1024 * 1024, "9_200MB_600MB"),
    (1 * 1024 * 1024 * 1024, "10_600MB_1GB"),
    (5 * 1024 * 1024 * 1024, "11_1GB_5GB"),
    (10 * 1024 * 1024 * 1024, "12_5GB_10GB"),
    (20 * 1024 * 1024 * 1024, "13_10GB_20GB"),
]

# --- Extension Categories ---
extension_categories = {
    "images": {"jpg", "jpeg", "avif", "webp", "png", "gif", "bmp", "tiff", "heif", "raw", "ico", "svg", "ppm", "pbm", "pgm"},
    "videos": {"mp4", "avi", "mov", "mkv", "flv", "webm", "wmv", "mpeg", "mpg", "3gp", "ogv", "m4v", "hevc", "h264", "h265", "vp8", "vp9", "f4v", "rm", "ram", "asf", "divx"},
    "audios": {"mp3", "aac", "ogg", "wma", "flac", "m4a", "opus", "wav", "aiff", "pcm", "alac", "au", "ra", "ape", "spx", "dts"},
    "documents": {"txt", "rtf", "md", "log", "csv", "tsv", "doc", "docx", "odt", "pages", "xls", "xlsx", "ppt", "pptx", "pdf", "tex", "bib", "sty", "epub", "mobi", "azw3"},
    "archives": {"zip", "tar", "gz", "rar", "7z", "tar.gz", "tar.bz2", "xz", "cab", "iso", "lzma", "tar.xz", "tar.lz"},
    "executables": {"exe", "bat", "msi", "com", "vbs", "sh", "bin", "out", "app", "dmg", "pkg"},
    "webfiles": {"html", "htm", "css", "js", "jsx", "ts", "tsx", "json", "php", "py", "rb", "pl", "jsp", "asp", "cfm", "xml", "yml", "xsl", "yaml"},
    "databases": {"sql", "db", "sqlite", "mdb", "accdb", "bson", "couchdb"},
    "fonts": {"ttf", "otf", "woff", "woff2", "fnt", "bdf"},
    "configs": {"conf", "ini", "cfg", "settings", "properties"},
    "backups": {"bak", "old", "swp", "~", "bk", "backup"},
    "cad": {"dwg", "dxf", "step", "iges", "stl", "gcode", "skp", "obj", "fbx", "dae", "blend", "3ds", "x3d"},
}

# --- Helpers ---
def get_size_category(file_size):
    for limit, name in size_categories:
        if file_size <= limit:
            return name
    return "14_over_20GB"

def get_extension_category(filename):
    if "." not in filename:
        return "others"
    ext = filename.rsplit(".", 1)[1].lower()
    for cat, exts in extension_categories.items():
        if ext in exts:
            return cat
    return "others"

def safe_destination(subdir, filename):
    dest = subdir / filename
    if not dest.exists():
        return dest
    stem, suffix = os.path.splitext(filename)
    hashpart = hashlib.sha1(filename.encode()).hexdigest()[:6]
    return subdir / f"{stem}_{hashpart}{suffix}"

# --- Organize Files ---
def organize_files(base_dir, dry_run=True):
    base_dir = Path(base_dir)
    organized_dir = base_dir / "organized"
    organized_dir.mkdir(exist_ok=True)

    all_files = []
    for root, _, files in os.walk(base_dir):
        root_path = Path(root)
        if organized_dir in root_path.parents or root_path == organized_dir:
            continue
        for file in files:
            file_path = root_path / file
            if file_path.is_symlink():
                print(f"Skipping symlink: {file_path}")
                continue
            all_files.append(file_path)

    counters = defaultdict(int)

    for file_path in all_files:
        if not file_path.is_file():
            continue

        file_size = file_path.stat().st_size
        size_cat = get_size_category(file_size)
        ext_cat = get_extension_category(file_path.name)

        target_dir = organized_dir / size_cat / ext_cat
        dir_number = counters[(size_cat, ext_cat)] // 1000
        subdir = target_dir / f"dir{dir_number}"
        subdir.mkdir(parents=True, exist_ok=True)

        destination = safe_destination(subdir, file_path.name)
        counters[(size_cat, ext_cat)] += 1

        if dry_run:
            print(f"[DRY RUN] Would move: {file_path} -> {destination}")
        else:
            shutil.move(str(file_path), str(destination))
            print(f"Moved: {file_path} -> {destination}")

    if not dry_run:
        cleanup_single_dir(organized_dir)

# --- Cleanup Step ---
def cleanup_single_dir(organized_dir):
    for size_cat in organized_dir.iterdir():
        if not size_cat.is_dir():
            continue
        for ext_cat in size_cat.iterdir():
            if not ext_cat.is_dir():
                continue
            dirs = [d for d in ext_cat.iterdir() if d.is_dir() and d.name.startswith("dir")]
            if len(dirs) == 1 and dirs[0].name == "dir0":
                dir0 = dirs[0]
                for f in dir0.iterdir():
                    target = ext_cat / f.name
                    if target.exists():
                        target = safe_destination(ext_cat, f.name)
                    shutil.move(str(f), str(target))
                dir0.rmdir()
                print(f"Flattened: {ext_cat}")

# --- Entry Point ---
if __name__ == "__main__":
    base_directory = os.path.abspath(sys.argv[1])
    dry_run = False  # Set to False to actually move
    organize_files(base_directory, dry_run=dry_run)
