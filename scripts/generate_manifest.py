import os
import json
import subprocess
from datetime import datetime

def get_last_commit_date_for_files(files, dirpath):
    last_commit_date = None
    
    for file in files:
        file_path = os.path.join(dirpath, file)
        try:
            # Get the last commit date for the individual file
            commit_date = subprocess.check_output(
                ['git', 'log', '-1', '--format=%cd', '--date=iso', file_path],
                stderr=subprocess.STDOUT
            ).strip().decode('utf-8')
            
            # Update last_commit_date to be the most recent of all the files
            if last_commit_date is None or commit_date > last_commit_date:
                last_commit_date = commit_date
        except subprocess.CalledProcessError:
            continue
    
    return last_commit_date

def get_manifest_data(instructions_dir):
    manifest = {'instructions': {}}

    for dirpath, dirnames, filenames in os.walk(instructions_dir):
        if filenames:
            # Get the last commit date based on the most recent change among the files
            last_modified = get_last_commit_date_for_files(filenames, dirpath)
        else:
            last_modified = None

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
