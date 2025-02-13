import requests
import json
import os

# === Configuration ===
# Replace these values with your actual Figma file key and your personal access token.
FILE_KEY = 'YOUR_FIGMA_FILE_KEY'
ACCESS_TOKEN = 'YOUR_FIGMA_ACCESS_TOKEN'

# === Functions ===
def fetch_figma_file(file_key, access_token):
    """
    Fetches the Figma file JSON data using the provided file key and access token.
    """
    url = f"https://api.figma.com/v1/files/{file_key}"
    headers = {"X-Figma-Token": access_token}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise Exception(f"Failed to fetch file: {response.status_code} {response.text}")
    
    return response.json()

def extract_relevant_metadata(node):
    """
    Recursively traverses a node and extracts relevant metadata for HTML/CSS generation.
    
    For each node, we extract:
      - id, name, and type
      - absoluteBoundingBox (layout info: x, y, width, height) if present
      - fills (colors or gradients) if available
      - style (font or stroke details) if available
      - text content (if it's a TEXT node)
      - children (recursively processed)
    
    You can extend or modify this extraction based on your needs.
    """
    filtered = {
        "id": node.get("id"),
        "name": node.get("name"),
        "type": node.get("type")
    }
    
    # Extract layout properties if available
    if "absoluteBoundingBox" in node:
        filtered["absoluteBoundingBox"] = node["absoluteBoundingBox"]
    
    # Extract fill information if available
    if "fills" in node:
        filtered["fills"] = node["fills"]
    
    # Extract style info if available (useful for TEXT nodes or shapes)
    if "style" in node:
        filtered["style"] = node["style"]
    
    # For text nodes, extract the characters property
    if node.get("type") == "TEXT" and "characters" in node:
        filtered["characters"] = node["characters"]
    
    # Recursively process children nodes if they exist
    if "children" in node:
        filtered_children = []
        for child in node["children"]:
            filtered_children.append(extract_relevant_metadata(child))
        filtered["children"] = filtered_children
    
    return filtered

def save_json_to_file(data, filename):
    """
    Saves JSON data to a file in the current directory.
    """
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    print(f"Saved {filename}")

# === Main Execution ===
if __name__ == '__main__':
    try:
        # 1. Fetch the raw data from Figma
        figma_data = fetch_figma_file(FILE_KEY, ACCESS_TOKEN)
        
        # 2. Save the raw JSON file
        raw_filename = os.path.join(os.getcwd(), "raw_figma.json")
        save_json_to_file(figma_data, raw_filename)
        
        # 3. Extract relevant metadata from the "document" node
        document = figma_data.get("document")
        if not document:
            raise Exception("The Figma file does not contain a 'document' node.")
        
        filtered_data = extract_relevant_metadata(document)
        
        # 4. Save the filtered JSON file
        filtered_filename = os.path.join(os.getcwd(), "filtered_figma.json")
        save_json_to_file(filtered_data, filtered_filename)
        
    except Exception as e:
        print(f"Error: {e}")
