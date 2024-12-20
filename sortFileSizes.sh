#!/bin/bash

# Define size ranges (in bytes)
sizes=( 51200 102400 204800 512000 1048576 2097152 5242880 10485760 52428800 104857600 209715200 524288000 1073741824 3221225472 5368709120 10737418240 21737418240 )
labels=("50KB" "100KB" "200KB" "500KB" "1MB" "2MB" "5MB" "10MB" "50MB" "100MB" "200MB" "500MB" "1GB" "3GB" "5GB" "10GB" "20GB")

# Function to create directories and move files
categorize_and_move() {
    # Create directories for each size range
    for label in "${labels[@]}"; do
        mkdir -p "$1/$label"
    done

    # Find files and move them to the correct directory based on size
    find "$1" -type f -exec du -b {} + | while read -r size file; do
        for i in "${!sizes[@]}"; do
            if (( size < ${sizes[$i]} )); then
                dest_dir="$1/${labels[$i]}"
                dest_file="$dest_dir/$(basename "$file")"

                # Check if a file with the same name already exists in the destination directory
                if [[ -e "$dest_file" ]]; then
                    # If file exists, generate a unique name by appending a suffix
                    base_name=$(basename "$file")
                    extension="${base_name##*.}"
                    name_without_extension="${base_name%.*}"

                    # Loop until we find a unique filename
                    counter=1
                    while [[ -e "$dest_dir/${name_without_extension}_$counter.$extension" ]]; do
                        ((counter++))
                    done

                    # Rename the file with the new unique name
                    dest_file="$dest_dir/${name_without_extension}_$counter.$extension"
                fi

                # Move the file to the destination
                mv "$file" "$dest_file"
                echo "Moved $file to $dest_file"
                break
            fi
        done
    done
}

# Call the function for the directory provided as argument (or current directory)
categorize_and_move "$1"

# Remove empty directories after files have been moved
find "$1" -type d -empty -exec rmdir {} \;

