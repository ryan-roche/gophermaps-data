import csv
import requests
from dotenv import load_dotenv
from os import getenv
from neo4j import GraphDatabase, graph

AREA_CSV_HEADERS = ['name', 'navid', 'apple-place-id', 'google-place-id']

# Authenticate to Neo4j
load_dotenv('secrets.env')
AURA_CONNECTION_URI = getenv("AURA_URI")
AURA_USERNAME = getenv("AURA_USERNAME")
AURA_PASSWORD = getenv("AURA_PASSWORD")
driver = GraphDatabase.driver(
    AURA_CONNECTION_URI,
    auth=(AURA_USERNAME, AURA_PASSWORD)
)

# Get area names from API
response = requests.get("https://api.gophermaps.xyz/areas")
if response.status_code == 200:
    data = response.json()
    areas = [area['name'] for area in data]

# Create CSV file of buildings for each area
for area in areas:
    with driver.session() as session:
        buildings_query = """
        MATCH (b:BuildingKey)
        WHERE b.area = $area
        RETURN b
        """
        result = session.run(buildings_query, area=area)
        buildings = [record['b'] for record in result]
        print(buildings[0]['navID'], buildings[0]['buildingName'])

    with open(f"GopherMaps Mapping - {area}.csv", 'w') as fp:
        writer = csv.writer(fp)
        writer.writerow(AREA_CSV_HEADERS)
        for building in buildings:
            writer.writerow([building['buildingName'], building['navID'], '', ''])

    
driver.close()

    