import os
import json
from datetime import datetime

def get_last_modified_time(directory_path):
    """Get the last modified time of the latest modified file in the directory."""
    latest_time = 0
    for dirpath, _, filenames in os.walk(directory_path):
        for file in filenames:
            file_path = os.path.join(dirpath, file)
            file_modified_time = os.path.getmtime(file_path)
            if file_modified_time > latest_time:
                latest_time = file_modified_time
    return datetime.utcfromtimestamp(latest_time).isoformat()

def generate_manifest(instructions_dir):
    manifest = {"instructions": {}}

    # Loop through each directory inside /instructions
    for dir_name in os.listdir(instructions_dir):
        dir_path = os.path.join(instructions_dir, dir_name)
        if os.path.isdir(dir_path):
            # List all files in the directory
            files = sorted(os.listdir(dir_path))

            # Get the last modified date of the directory
            last_modified = get_last_modified_time(dir_path)

            # Add this directory's info to the manifest
            manifest["instructions"][dir_name] = {
                "last_modified": last_modified,
                "files": files
            }

    # Save the manifest.json file
    with open("manifest.json", "w") as f:
        json.dump(manifest, f, indent=4)

if __name__ == "__main__":
    generate_manifest("./instructions")
