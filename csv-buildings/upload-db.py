import csv

from dotenv import load_dotenv
from os import getenv
from neo4j import GraphDatabase, graph

# Load secrets from an env file bc I'm not about to accidentally put database credentials in source control again :D
load_dotenv('secrets.env')

# Load environment variables into python vars
AURA_CONNECTION_URI = getenv("AURA_URI")
AURA_USERNAME = getenv("AURA_USERNAME")
AURA_PASSWORD = getenv("AURA_PASSWORD")


# Establish database connection
driver = GraphDatabase.driver(
    AURA_CONNECTION_URI,
    auth=(AURA_USERNAME, AURA_PASSWORD)
)


# Helper function for creating graph db nodes from csv rows
def create_node(tx, row):
    # Start with the Building label for every node
    labels = "Building"

    # Add BuildingKey label if 'buildingKey?' is 'y'
    if row['buildingKey?'].lower() == 'y':
        labels += ":BuildingKey"

    # Remove the 'buildingKey?' field from the row since it's not a node property
    properties = {k: v for k, v in row.items() if k != 'buildingKey?'}

    # Construct the Cypher query with dynamic labels and properties
    query = f"""
    CREATE (n:{labels} {{ {', '.join([f'{key}: ${key}' for key in properties])} }})
    """

    # Execute the query with parameters
    tx.run(query, **properties)

    # Print the query and the parameters (preview)
    # print("Cypher Query:", query)
    # print("Parameters:", properties)
    # print("-" * 50)


# Helper function for creating graph edges from csv rows
def create_edge(tx, row):
    # Construct the Cypher query
    query = """
    MATCH (a {navID: $A}), (b {navID: $B})
    CREATE (a)-[r:%s]->(b)
    """ % row['type']

    # Execute the query with parameters
    tx.run(query, A=row['A'], B=row['B'])

    # print("Cypher Query:", query)
    # print("Parameters:", {"A": row['A'], "B": row['B']})
    # print("-" * 50)


# Create nodes using the buildings CSV file
with open('GopherMaps Buildings - St Paul.csv', mode='r') as file:
    csv_reader = csv.DictReader(file)

    with driver.session() as session:
        for line in csv_reader:
            session.write_transaction(create_node, line)


# Create edges using the edges CSV file
with open('GopherMaps Buildings - St Paul Edges.csv', mode='r') as file:
    csv_reader = csv.DictReader(file)

    with driver.session() as session:
        for line in csv_reader:
            session.write_transaction(create_edge, line)


driver.close()
