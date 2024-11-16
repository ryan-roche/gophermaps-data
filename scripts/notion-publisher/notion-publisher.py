import dotenv, os
from notion2md.exporter.block import MarkdownExporter

dotenv.load_dotenv("secrets.env")
token = os.getenv("NOTION_TOKEN")

MarkdownExporter(block_url='https://www.notion.so/ryan-roche/kh4-me2-13e5af49bf2f816fb4c6f5c8b073b3e1?pvs=4',
                 token=token, unzipped=True).export()

# TODO download all images from the markdown file, sequentially naming them

# TODO replace image paths in markdown with local paths

# TODO create zip of markdown files

# TODO create PR on github repo
