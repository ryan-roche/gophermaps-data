# Downloads the contents of a notion page, generates the proper directory structure for the instructions, and commits them to GitHub
import base64
import json
import os
import re
import requests
from discord_webhook import DiscordWebhook, DiscordEmbed
from notion2md.exporter.block import MarkdownExporter

IMAGE_EMBED_REGEX = re.compile(r'!\[.*?\]\(.*?\)')
WEBHOOK_AVATAR_URL = "https://github.com/ryan-roche/gophermaps-data/blob/main/webhook-icons/gw-lambda.png?raw=true"


def main():
    return


def lambda_handler(event, context):

    edge_id = event["data"]["properties"]["Edge ID"]["title"][0]["plain_text"]
    page_url = event["data"]["url"]

    writer_name = event["data"]["properties"]["Writer"]["people"][0]["name"]
    writer_avatar_url = event["data"]["properties"]["Writer"]["people"][0]["avatar_url"]

    # Get the Notion Token from Parameter Store
    ssm = boto3.client('ssm')
    response = ssm.get_parameter(Name='/GopherMaps/NotionToken')
    os.environ['NOTION_TOKEN'] = response['Parameter']['Value']

    wh = post_discord_webhook(edge_id, writer_name, writer_avatar_url)

    download_page(page_url, edge_id)
    format_markdown(edge_id)
    sha = commit_to_github(edge_id)
    update_page_status(page_url)

    webhook_report_status(wh, edge_id, True, sha)

    response = {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"message": "Webhook received"})
    }

    return response


# MARK: Helpers for working with Notion
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

def update_page_status(page_url):
    token = os.environ['NOTION_TOKEN']

    last_part = page_url.split("/")[-1]
    last_part = last_part.split("?")[0]
    page_id = last_part[-32:]

    print(page_id)
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    update_data = {
        "properties": {
            "Status": { "select": {"name": "Uploaded"} }
        }
    }

    url = f"https://api.notion.com/v1/pages/{page_id}"
    response = requests.patch(url, json=update_data, headers=headers)

    print(response.json())


# MARK: Helpers for Discord Webhook
class DiscordEmbedColor:
    """
    Semantic colors for webhook messages
    """
    ERROR = 0xc40000
    INFO = 0x0085ff
    SUCCESS = 0x0eb400

def post_discord_webhook(edge_id, author_name, author_icon_url):
    DISCORD_WEBHOOK_URL = os.environ['DISCORD_WEBHOOK_URL']
    WEBHOOK_AVATAR_URL = "https://github.com/ryan-roche/gophermaps-data/blob/main/webhook-icons/gw-lambda.png?raw=true"

    wh = DiscordWebhook(
        url=DISCORD_WEBHOOK_URL,
        username="GopherMaps Lambda",
        avatar_url=WEBHOOK_AVATAR_URL,
    )

    # Build embed
    embed = DiscordEmbed(
        title = "Processing Instructions",
        description = f"Processing instruction files for {edge_id}",
        color = DiscordEmbedColor.INFO,
        footer = {
            "text": author_name,
            "icon_url": author_icon_url
        }
    )

    # Send to webhook
    wh.add_embed(embed)
    wh.execute()

    return wh

def webhook_report_status(webhook, edge_id, success, commit_sha):
    webhook.embeds[0]['color'] = DiscordEmbedColor.SUCCESS if success else DiscordEmbedColor.ERROR
    webhook.embeds[0]['title'] = "Instructions Processed" if success else "Error Processing Instructions"
    webhook.embeds[0]['description'] = f"Instructions for {edge_id} processed successfully" if success else f"Error processing instructions for {edge_id}"
    webhook.embeds[0]['author'] = {
        "name": f"Commit SHA {commit_sha}",
        "url": f"https://github.com/ryan-roche/gophermaps-data/commits/{commit_sha}",
        "icon_url": "https://github.com/github.png"
    }
    webhook.edit()
