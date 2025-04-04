# gophermaps-data

This repository is being used as a surrogate CDN for the Gophermaps project.

[![Generate manifest.json](https://github.com/ryan-roche/gophermaps-data/actions/workflows/manifest-generator.yml/badge.svg?branch=main)](https://github.com/ryan-roche/gophermaps-data/actions/workflows/manifest-generator.yml)

## Manifest

The key file in this repository is the `manifest.json`. It consists of two main components- a list of edges with instrutions available, and server announcement messages.

A webhook in the Social Coding discord is posted to with the status of each run of the manifest-generation task.

### Instructions List

The dictionary of instructions is automatically generated by a GitHub Actions runner using the `get_instructions_entry` method of `/scripts/generate_manifest.py`. For each directory in the `/instructions` subdirectory of the repository, it will add a key with the edge name (format specified below), and the value being a dictionary with keys
- "last_modified": an ISO-formatted date string containing the last time the instructions were updated, for use in the app to tell when downloaded instructions are out-of-date
- "files": a list of all files in the directory, so the app knows what files for the instructions must be downloaded

### Server Messages

The serverMessages array is also automatically generated using the contents of the `/serverMessages` subdirectory. Currently, instrutions must be hand-written following a specific format, but an interactive developer site is being worked on to simplify the process of writing the messages.

Server Messages are given both a start date and end date.
- Messages whose end dates have already passed will not be added to the manifest when it is generated, but the manifest is only regenerated when files in the repository are added to or modified, so the manifest may contain expired messages. Thus, the app must check message expiry dates before displaying them
- Messages whose start dates have not yet come *will* be added to the manifest, so future messages may be "loaded up" in advance

## Instructions

Instructions are each given their own directory, named in the format `{start-navID}-{end-navID}` and contain
1. A file named `instructions.md` containing the images with corresponding instructions in the alt text
2. Image files linked in the `instructions.md` file

Instructions are written in the Notion database, then automatically converted into the format specified above and Pull-Requested into the repository by an automated system once their contents are approved. 
