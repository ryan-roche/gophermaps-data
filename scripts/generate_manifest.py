import os
import json
import subprocess

# Get the absolute path of the directory where the script is located
script_dir = os.path.dirname(os.path.realpath(__file__))

# Get the path to the instructions directory relative to the script's location
instructions_directory = os.path.join(script_dir, '../instructions')


def get_last_commit_date_for_files(dirpath):
    latest_commit_date = None

    # Iterate over all files in the directory (recursively)
    for root, dirs, files in os.walk(dirpath):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                # Get the last commit date for the file
                commit_date = subprocess.check_output(
                    ['git', 'log', '-1', '--format=%cd', '--date=iso', '--', file_path],
                    stderr=subprocess.STDOUT
                ).strip().decode('utf-8')

                # Update the latest commit date if the new one is more recent
                if latest_commit_date is None or commit_date > latest_commit_date:
                    latest_commit_date = commit_date
            except subprocess.CalledProcessError:
                continue

    return latest_commit_date


def get_manifest_data(instructions_dir):
    manifest = {'instructions': {}}

    for dirpath, dirnames, filenames in os.walk(instructions_dir):
        # Skip the root directory itself
        if dirpath == instructions_dir:
            continue

        # Get the last modified date based on files in the directory
        last_modified = get_last_commit_date_for_files(dirpath)

        # Extract the directory name
        dir_name = os.path.basename(dirpath)

        # Store the directory's information
        manifest['instructions'][dir_name] = {
            'last_modified': last_modified,
            'files': filenames
        }

    return manifest


if __name__ == "__main__":
    # Ensure the instructions directory exists
    if os.path.exists(instructions_directory):
        # Generate the manifest data
        manifest_data = get_manifest_data(instructions_directory)

        # Write the output to the root directory
        manifest_path = os.path.join(script_dir, '../manifest.json')
        with open(manifest_path, 'w') as f:
            json.dump(manifest_data, f, indent=2)
    else:
        print(f"Error: {instructions_directory} does not exist.")
