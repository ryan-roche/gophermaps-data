import csv
from dotenv import load_dotenv
from os import getenv, path
from neo4j import GraphDatabase

area_csv_files = [
    {
        "filename": "GopherMaps Place IDs - GopherMaps Mapping - East Bank.csv",
        "areaName": "East Bank"
    },
    {
        "filename": "GopherMaps Place IDs - GopherMaps Mapping - West Bank.csv",
        "areaName": "West Bank"
    },
    {
        "filename": "GopherMaps Place IDs - GopherMaps Mapping - St Paul Campus.csv",
        "areaName": "St Paul Campus"
    }
]

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

driver.verify_connectivity()


# Helper function for setting place id node values
def add_place_ids(tx, row):
    query = """
    MATCH (n {navID: $A})
    SET n.applePlaceID = $B
    SET n.googlePlaceID = $C
    """
    tx.run(query, A=row['navid'], B=row['apple-place-id'], C=row['google-place-id'])
    print(f"✔ {row['navid']}")


for area in area_csv_files:
    print(f"Processing Nodes for {area['areaName']}")

    with open(area['filename']) as csvfile:
        reader = csv.DictReader(csvfile)

        with driver.session() as session:
            for row in reader:
                session.write_transaction(add_place_ids, row)

    print(f"Done processing Nodes for {area['areaName']}\n")
