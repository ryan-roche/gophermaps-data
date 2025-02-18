import os
from dotenv import load_dotenv
from mdutils import *
from notion2md.exporter.block import MarkdownExporter
import re

TEST_PAGE_URL = "https://www.notion.so/pwb2-hsec2-13e5af49bf2f8125919be7b2611f3827"
IMAGE_EMBED_REGEX = re.compile(r'!\[.*?\]\(.*?\)')


def download_page(page_url, edge_id):
    # Ensure the download directory is empty
    download_dir = os.path.join(os.getcwd(), edge_id)
    if os.path.exists(download_dir):
        for root, dirs, files in os.walk(download_dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(download_dir)

    # Download the "raw" page contents from Notion
    MarkdownExporter(block_url=page_url, download=True, output_filename="raw", output_path=os.path.join(os.getcwd(), edge_id), unzipped=True).export()


def format_markdown(edge_id):
    # Open the raw markdown file
    raw_md_path = os.path.join(os.getcwd(), edge_id, 'raw.md')
    new_md_path = os.path.join(os.getcwd(), edge_id, 'instructions.md')
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


def commit_to_github():
    return


if __name__ == "__main__":
    load_dotenv()
    download_page(TEST_PAGE_URL, "test1")
    format_markdown("test1")
