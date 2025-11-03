
import chromadb
import os
import xml.etree.ElementTree as ET

# Initialize the ChromaDB client
client = chromadb.PersistentClient(path="robot_db")

# Create or get the collection
collection = client.get_or_create_collection("robots")

def get_all_robots_from_output_folder():
    """
    This function will get all the .robot files from the output folder.
    """
    robot_files = []
    for filename in os.listdir("output"):
        if filename.endswith(".robot"):
            robot_files.append(os.path.join("output", filename))
    return robot_files

def add_robot_to_db(robot_file):
    """
    This function will add a robot to the ChromaDB database.
    """
    try:
        with open(robot_file, "r") as f:
            robot_content = f.read()
        
        # Use the filename as the id
        robot_id = os.path.basename(robot_file)

        # Add the robot to the collection
        collection.add(
            documents=[robot_content],
            ids=[robot_id]
        )
        return f"Robot {robot_id} added to the database."
    except Exception as e:
        return f"Error adding robot to database: {e}"

def query_robots(query_text, n_results=3):
    """
    This function will query the ChromaDB database for robots similar to the query_text.
    """
    try:
        results = collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        return results['documents']
    except Exception as e:
        return f"Error querying robots: {e}"
