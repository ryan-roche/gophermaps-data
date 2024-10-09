import os
import json
import subprocess
from datetime import datetime

def get_last_commit_date(path):
    try:
        # Get the last commit date for the files in the directory
        last_commit_date = subprocess.check_output(
            ['git', 'log', '-1', '--format=%cd', '--date=iso', path],
            stderr=subprocess.STDOUT
        ).strip().decode('utf-8')
        return last_commit_date
    except subprocess.CalledProcessError:
        return None

def get_manifest_data(instructions_dir):
    manifest = {'instructions': {}}

    for dirpath, dirnames, filenames in os.walk(instructions_dir):
        # Get the last commit date for the directory
        last_modified = get_last_commit_date(dirpath)

        # Extract the directory name from the path
        dir_name = os.path.basename(dirpath)
        
        manifest['instructions'][dir_name] = {
            'last_modified': last_modified,
            'files': filenames
        }

    return manifest

if __name__ == "__main__":
    instructions_directory = 'instructions'
    manifest_data = get_manifest_data(instructions_directory)

    # Write to manifest.json
    with open('manifest.json', 'w') as f:
        json.dump(manifest_data, f, indent=2)
