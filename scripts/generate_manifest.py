from datetime import datetime, timezone
import os
import json
import hashlib
import subprocess

# Get the absolute path of the directory where the script is located
script_dir = os.path.dirname(os.path.realpath(__file__))

# Get the path to the instructions and serverMessages directories relative to the script's location
instructions_directory = os.path.join(script_dir, '../instructions')
server_messages_directory = os.path.join(script_dir, '../serverMessages')


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


def get_instructions_entry(instructions_dir):
    instructions = {}

    for dirpath, dirnames, filenames in os.walk(instructions_dir):
        # Skip the root directory itself
        if dirpath == instructions_dir:
            continue

        # Get the last modified date based on files in the directory
        last_modified = get_last_commit_date_for_files(dirpath)

        # Extract the directory name
        dir_name = os.path.basename(dirpath)

        # Store the directory's information
        instructions[dir_name] = {
            'last_modified': last_modified,
            'files': filenames
        }

    return instructions


def generate_content_hash(content):
    # Convert the message content into a JSON string, ensuring consistent key order
    message_str = json.dumps(content, sort_keys=True)
    # Create a SHA-256 hash of the JSON string
    return hashlib.sha256(message_str.encode('utf-8')).hexdigest()


def get_server_messages_entry(server_messages_dir):
    server_messages = []
    current_time = datetime.now(timezone.utc)

    for filename in os.listdir(server_messages_dir):
        file_path = os.path.join(server_messages_dir, filename)

        if os.path.isfile(file_path) and filename.endswith('.json'):
            try:
                # Read and parse the JSON content of the file
                with open(file_path, 'r') as file:
                    content = json.load(file)
                    # Parse the endDate as a datetime object
                    end_date = datetime.fromisoformat(content.get('endDate'))

                    # Check if the endDate is in the future
                    if end_date > current_time:
                        # Generate a content-based hash ID for the message
                        message_id = generate_content_hash(content)
                        content['id'] = message_id  # Add the ID to the message
                        server_messages.append(content)
                        print(f"Included message from {file_path} with ID {message_id}")
                    else:
                        print(f"Excluded message from {file_path} due to past endDate {content.get('endDate')}")
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON from {file_path}: {e}")
            except Exception as e:
                print(f"Error reading {file_path}: {e}")

    return server_messages


def get_manifest_data():
    manifest = {}

    # Process the instructions directory
    if os.path.exists(instructions_directory):
        manifest['instructions'] = get_instructions_entry(instructions_directory)
    else:
        print(f"Error: {instructions_directory} does not exist.")

    # Process the serverMessages directory
    if os.path.exists(server_messages_directory):
        manifest['serverMessages'] = get_server_messages_entry(server_messages_directory)
    else:
        print(f"Error: {server_messages_directory} does not exist.")

    return manifest


if __name__ == "__main__":
    # Generate the manifest data
    manifest_data = get_manifest_data()

    # Write the output to the root directory
    manifest_path = os.path.join(script_dir, '../manifest.json')
    with open(manifest_path, 'w') as f:
        json.dump(manifest_data, f, indent=2)
