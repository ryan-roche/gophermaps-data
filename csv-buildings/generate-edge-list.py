import csv
from dotenv import load_dotenv
from os import getenv
from neo4j import GraphDatabase, graph

# Load database credentials from env file
load_dotenv('secrets.env')
AURA_CONNECTION_URI = getenv("AURA_URI")
AURA_USERNAME = getenv("AURA_USERNAME")
AURA_PASSWORD = getenv("AURA_PASSWORD")

# Establish database connection
driver = GraphDatabase.driver(
    AURA_CONNECTION_URI,
    auth=(AURA_USERNAME, AURA_PASSWORD)
)


def main():
    # Get list of unique areas
    return
