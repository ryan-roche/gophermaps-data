# Downloads the contents of a notion page, generates the proper directory structure for the instructions, and commits them to GitHub
import base64
import boto3
import json
import os
import requests
from discord_webhook import DiscordWebhook, DiscordEmbed
from notion2md.exporter.block import MarkdownExporter


def lambda_handler(event, context):
    page_data = json.loads(event["body"])

    edge_id = event["data"]["properties"]["Edge ID"]["title"][0]["plain_text"]
    page_url = event["data"]["url"]

    print(edge_id)
    print(page_url)


    response = {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"message": "Webhook received"})
    }

    return response


# MARK: Helpers for downloading and formatting Notion page
def download_page(page_url, edge_id):
    # Ensure the download directory is empty
    download_dir = f"/tmp/{edge_id}"
    if os.path.exists(download_dir):
        for root, dirs, files in os.walk(download_dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(download_dir)

    # Download the "raw" page contents from Notion
    MarkdownExporter(block_url=page_url, download=True, output_filename="raw", output_path=download_dir, unzipped=True).export()

def format_markdown(edge_id):
    # Open the raw markdown file
    raw_md_path = os.path.join(f"/tmp/{edge_id}", 'raw.md')
    new_md_path = os.path.join(f"/tmp/{edge_id}", 'instructions.md')
    new_file_lines = []

    # Parse the information from the raw Notion page markdown
    with open(raw_md_path, 'r') as file:
        raw_image_line = None
        for line in file:
            stripped_line = line.strip()

            # Skip the blank lines
            if stripped_line == "":
                continue

            if IMAGE_EMBED_REGEX.match(stripped_line):
                raw_image_line = stripped_line
            elif raw_image_line:
                new_image_line = re.sub(r'!\[.*?\]', f'![{stripped_line}]', raw_image_line)
                new_file_lines.append(new_image_line + '\n')
                raw_image_line = None

    # Write the new, formatted markdown file
    with open(new_md_path, 'w') as file:
        file.writelines(new_file_lines)

    # Remove the old, "raw" markdown
    os.remove(raw_md_path)

    return


# MARK: Helper for commiting files to GitHub
def commit_to_github(edge_id: str):
    TOKEN = ""  # TODO replace with parameter store value
    OWNER = "ryan-roche"
    REPO = "gophermaps-data"
    BRANCH = "testing"
    HEADERS = {"Authorization": f"token {TOKEN}"}


    local_dir = f"/tmp/{edge_id}"
    remote_dir = f"instructions/{edge_id}"

    if not os.path.exists(local_dir):
        raise FileNotFoundError(f"Local directory {local_dir} does not exist")

    # Step 1: Get the latest commit SHA
    latest_commit_sha = requests.get(
        f"https://api.github.com/repos/{OWNER}/{REPO}/git/ref/heads/{BRANCH}",
        headers=HEADERS
    ).json()["object"]["sha"]

    # Step 2: Get the base tree SHA
    latest_tree_sha = requests.get(
        f"https://api.github.com/repos/{OWNER}/{REPO}/git/commits/{latest_commit_sha}",
        headers=HEADERS
    ).json()["tree"]["sha"]

    # Step 3: Prepare tree entries
    tree_entries = []
    for root, _, files in os.walk(local_dir):
        for file in files:
            local_path = os.path.join(root, file)
            remote_path = os.path.join(remote_dir, os.path.relpath(local_path, local_dir))

            # Read and encode file content
            with open(local_path, "rb") as f:
                content = base64.b64encode(f.read()).decode("utf-8")

            tree_entries.append({
                "path": remote_path,
                "mode": "100644",
                "type": "blob",
                "content": content
            })

    # Step 4: Create a new tree
    new_tree = requests.post(
        f"https://api.github.com/repos/{OWNER}/{REPO}/git/trees",
        headers=HEADERS,
        json={"base_tree": latest_tree_sha, "tree": tree_entries}
    ).json()

    # Step 5: Create a new commit
    commit_data = {
        "message": f"Add instructions for {edge_id}",
        "tree": new_tree["sha"],
        "parents": [latest_commit_sha],
        "author": {
            "name": "GopherMaps Lambda",  # Replace with the name you want
            "email": "coding@umn.edu"  # Replace with the email you want
        }
    }

    new_commit = requests.post(
        f"https://api.github.com/repos/{OWNER}/{REPO}/git/commits",
        headers=HEADERS,
        json=commit_data
    ).json()

    # Step 6: Update branch reference
    requests.patch(
        f"https://api.github.com/repos/{OWNER}/{REPO}/git/refs/heads/{BRANCH}",
        headers=HEADERS,
        json={"sha": new_commit["sha"]}
    )


# MARK: Helpers for Discord Webhook
class DiscordEmbedColor:
    """
    Semantic colors for webhook messages
    """
    ERROR = 0xc40000
    INFO = 0x0085ff
    SUCCESS = 0x0eb400

def post_discord_webhook(edge_id):
    DISCORD_WEBHOOK_URL = "" # TODO replace with parameter store value
    WEBHOOK_AVATAR_URL = "https://github.com/ryan-roche/gophermaps-data/blob/main/webhook-icons/gw-lambda.png?raw=true"

    wh = DiscordWebhook(url=DISCORD_WEBHOOK_URL, username="GopherMaps Lambda", avatar_url=WEBHOOK_AVATAR_URL)

    # Build embed
    embed = DiscordEmbed(
        title = "Processing Instructions",
        description = f"Processing instruction files for {edge_id}",
        color = DiscordEmbedColor.INFO
    )

    # Send to webhook
    wh.add_embed(embed)
    wh.execute()

    return wh

def webhook_report_status(webhook, edge_id, success):
    webhook.embeds[0]['color'] = DiscordEmbedColor.SUCCESS if success else DiscordEmbedColor.ERROR
    webhook.embeds[0]['title'] = "Instructions Processed" if success else "Error Processing Instructions"
    webhook.embeds[0]['description'] = f"Instructions for {edge_id} processed successfully" if success else f"Error processing instructions for {edge_id}"
    webhook.edit()
