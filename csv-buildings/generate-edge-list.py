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

driver.verify_connectivity()


def get_unique_areas(tx):
    result = tx.run("""
        MATCH (n) 
        WHERE n.area IS NOT NULL
        RETURN DISTINCT n.area
    """)
    # Convert to list of values
    return [record["n.area"] for record in result]


def get_unique_edges(tx, area):
    result = tx.run(f"""
    MATCH path = (n1)-[r]->(n2)
    WHERE n1.area = '{area}'
    AND n2.area = '{area}'
    RETURN [node in nodes(path) | [node.buildingName, node.floor, node.navID]] as nodePair
    """)
    # Convert to a list
    return [record.get('nodePair') for record in result]


def write_edges_file(edges, area):
    def _edge_navid(edge):
        return f"{edge[0][2]}-{edge[1][2]}"

    def _edge_line(edge):
        return [edge[0][0], edge[0][1], edge[1][0], edge[1][1], _edge_navid(edge)]

    filename = f"{area}-edges.csv"
    print(f"Writing file for {area}...", end=" ", flush=True)
    with open(filename, 'w') as csvfile:
        writer = csv.writer(csvfile)
        for edge in edges:
            reversed_edge = edge[::-1]
            writer.writerow(_edge_line(edge))
            writer.writerow(_edge_line(reversed_edge))
    print("done.", flush=True)


# Get list of unique areas
with driver.session() as session:
    areas = session.execute_read(get_unique_areas)
    print(f"Found Areas: {areas}")
    print("Excluding Test Buildings.", end=" ")
    areas.remove("Test Buildings")
    print(f"Filtered Buildings: {areas}")

    print("----------")

    print("Testing edge list generation with Test Buildings:")
    testEdges = session.execute_read(get_unique_edges, "Test Buildings")
    print(testEdges)
    print(f"{len(testEdges)} unique, directional edges. This should be five!")
    write_edges_file(testEdges, "Test Buildings")

    print("==========")

    for area in areas:
        area_edges = session.execute_read(get_unique_edges, area)
        write_edges_file(area_edges, area)
        print("----------")

    print("Done!")


driver.close()
