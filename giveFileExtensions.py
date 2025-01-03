import os,sys
import magic
import random
import string

# Expanded list of common valid extensions
VALID_EXTENSIONS = set([
    ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp", 
    ".txt", ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".csv", 
    ".ppt", ".pptx", ".mp3", ".wav", ".ogg", ".flac", 
    ".mp4", ".avi", ".mkv", ".mov", ".wmv", ".webm", 
    ".zip", ".rar", ".7z", ".tar", ".gz", ".iso", ".exe", 
    ".html", ".htm", ".css", ".js", ".json", ".xml", ".php", 
    ".py", ".java", ".c", ".cpp", ".rb", ".go", ".sh"
])

def is_valid_extension(filename):
    """Check if the file has a valid extension."""
    _, ext = os.path.splitext(filename)
    return ext.lower() in VALID_EXTENSIONS

def sanitize_filename(filename):
    """Remove query strings and sanitize the filename."""
    return filename.split('?')[0]

def generate_random_filename(extension=""):
    """Generate a random 7-character filename with an optional extension."""
    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=7))
    return f"{random_string}{extension}"

def detect_file_type(file_path):
    """Detect file type using python-magic."""
    mime = magic.Magic(mime=True)
    mime_type = mime.from_file(file_path)
    return mime_type

def mime_to_extension(mime_type):
    """Map MIME types to file extensions."""
    mime_extension_map = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/gif": ".gif",
        "image/bmp": ".bmp",
        "image/tiff": ".tiff",
        "image/webp": ".webp",
        "text/plain": ".txt",
        "application/pdf": ".pdf",
        "application/msword": ".doc",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
        "application/vnd.ms-excel": ".xls",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": ".xlsx",
        "application/vnd.ms-powerpoint": ".ppt",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation": ".pptx",
        "audio/mpeg": ".mp3",
        "audio/wav": ".wav",
        "audio/ogg": ".ogg",
        "video/mp4": ".mp4",
        "video/x-msvideo": ".avi",
        "video/x-matroska": ".mkv",
        "video/quicktime": ".mov",
        "application/zip": ".zip",
        "application/x-rar-compressed": ".rar",
        "application/x-7z-compressed": ".7z",
        "application/x-tar": ".tar",
        "application/gzip": ".gz",
        "application/octet-stream": ".iso",
        "text/html": ".html",
        "text/css": ".css",
        "application/javascript": ".js",
        "application/json": ".json",
        "application/xml": ".xml",
        "text/x-python": ".py",
    }
    return mime_extension_map.get(mime_type, None)

def add_extensions_to_files(directory):
    # List all files in the directory
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)

        # Skip directories
        if os.path.isdir(file_path):
            continue

        # Sanitize the filename by removing query strings
        sanitized_filename = sanitize_filename(filename)
        sanitized_file_path = os.path.join(directory, sanitized_filename)
        if sanitized_filename != filename:
            os.rename(file_path, sanitized_file_path)
            file_path = sanitized_file_path
            print(f"Sanitized: {filename} -> {sanitized_filename}")

        # Check if the file already has a valid extension
        if is_valid_extension(sanitized_filename):
            continue

        # Detect file type using python-magic
        mime_type = detect_file_type(file_path)
        if mime_type:
            extension = mime_to_extension(mime_type)
            if extension:
                # Generate a random filename with the correct extension
                new_filename = generate_random_filename(extension)
                new_file_path = os.path.join(directory, new_filename)
                os.rename(file_path, new_file_path)
                print(f"Renamed: {file_path} -> {new_file_path}")
            else:
                print(f"Unknown MIME type: {mime_type} for file {file_path}")
        else:
            # Generate a random filename without an extension if type is unknown
            new_filename = generate_random_filename()
            new_file_path = os.path.join(directory, new_filename)
            os.rename(file_path, new_file_path)
            print(f"Renamed (unknown type): {file_path} -> {new_file_path}")

# Directory to scan
directory_path = os.path.abspath(sys.argv[1])
add_extensions_to_files(directory_path)
