import requests
import sys
import json
import yaml

def load_character_ids(filepath):
    with open(filepath, 'r') as file:
        data = yaml.safe_load(file)
    return {character['name']: character['id'] for character in data['characters']}

def update_character_sheet(character_id):
    url = f"https://character-service.dndbeyond.com/character/v5/character/{character_id}"
    try:
        # Make the GET request
        response = requests.get(url)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        character_data = response.json()

        if character_data['success']:  # Check if the API call was successful
            return character_data
        else:
            raise Exception(f"Failed to update character sheet: {character_data['message']}")
    except requests.RequestException as e:
        raise Exception(f"API request failed: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python fetch_character_data.py <character_name>")
        sys.exit(1)

    character_name = sys.argv[1]
    character_ids = load_character_ids('characters.yml')

    if character_name not in character_ids:
        print(f"Character name '{character_name}' not found.")
        sys.exit(1)

    character_id = character_ids[character_name]
    try:
        character_data = update_character_sheet(character_id)
        print("Character sheet updated successfully:")
        print(json.dumps(character_data, indent=4))
    except Exception as e:
        print(str(e))