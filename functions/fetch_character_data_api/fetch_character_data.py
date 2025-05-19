import requests
import os
import json
import yaml
from bs4 import BeautifulSoup

## Set Local Variables
CHARACTERS_YML = os.path.join(os.path.dirname(__file__), "characters.yml")
OUTPUT_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../halls-of-the-damned/CHARACTERS")
)
TEMP_DIR = os.path.join(os.path.dirname(__file__), "temp")
JSON_OUTPUT_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../halls-of-the-damned/CHARACTERS/json")
)

# Function to Load Characters from CHARACTERS_YML
def load_characters(filepath):
    with open(filepath, 'r') as file:
        data = yaml.safe_load(file)
    return data['characters']

def fetch_character_json(character_id):
    url = f"https://character-service.dndbeyond.com/character/v5/character/{character_id}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises an HTTPError for bad responses

        
        print(f"Fetched data for ID {character_id}")
        return response.json()
        
    except requests.RequestException as e:
        print(f"API request failed for ID {character_id}: {str(e)}")
        return None

def update_character_sheet(character_id):
    try:
        # Make the GET request

        if character_data['success']:  # Check if the API call was successful
            # Parse the data
            character = character_data['data']
            character_sheet = {
                'id': character['id'],
                'user_id': character['userId'],
                'username': character['username'],
                'is_assigned_to_player': character['isAssignedToPlayer'],
                'readonly_url': character['readonlyUrl'],
                'avatar_url': character['decorations']['avatarUrl'],
                'frame_avatar_url': character['decorations']['frameAvatarUrl'],
                'small_backdrop_avatar_url': character['decorations']['smallBackdropAvatarUrl'],
                'large_backdrop_avatar_url': character['decorations']['largeBackdropAvatarUrl'],
                'name': character['name'],
                'social_name': character['socialName'],
                'gender': character['gender'],
                'faith': character['faith'],
                'age': character['age'],
                'hair': character['hair'],
                'eyes': character['eyes'],
                'skin': character['skin'],
                'height': character['height'],
                'weight': character['weight'],
                'inspiration': character['inspiration'],
                'base_hit_points': character['baseHitPoints'],
                'stats': {stat['id']: stat['value'] for stat in character['stats']},
                'background_name': character['background']['definition']['name'],
                'background_description': character['background']['definition']['description'],
                'race_full_name': character['race']['fullName'],
                'race_description': character['race']['description'],
                'inventory': [{
                    'item_id': item['id'],
                    'item_name': item['definition']['name'],
                    'item_type': item['definition']['type'],
                    'equipped': item['equipped']
                } for item in character['inventory']],
                'notes_allies': character['notes']['allies'],
                'notes_personal_possessions': character['notes']['personalPossessions'],
                'personality_traits': character['traits']['personalityTraits'],
                'ideals': character['traits']['ideals'],
                'bonds': character['traits']['bonds'],
                'flaws': character['traits']['flaws'],
                'use_homebrew_content': character['preferences']['useHomebrewContent']
            }

            return character_sheet
        else:
            raise Exception(f"Failed to update character sheet: {character_data['message']}")
    except requests.RequestException as e:
        raise Exception(f"API request failed: {str(e)}")

def print_character_sheet(character_sheet):
    for key, value in character_sheet.items():
        if isinstance(value, dict):
            print(f"{key}:")
            for sub_key, sub_value in value.items():
                print(f"  {sub_key}: {sub_value}")
        elif isinstance(value, list):
            print(f"{key}:")
            for item in value:
                if isinstance(item, dict):
                    print("  -")
                    for item_key, item_value in item.items():
                        print(f"    {item_key}: {item_value}")
                else:
                    print(f"  - {item}")
        else:
            print(f"{key}: {value}")

def render_markdown(character_data):
    data = character_data['data']
    avatar_url = data.get('decorations', {}).get('avatarUrl', '')
    player = data.get('player', '')
    race = data.get('race', {}).get('baseRaceName', '')
    classes = data.get('classes', [])
    resistances = ""  # Fill as needed
    # Ability scores
    stats = {stat['id']: stat['value'] for stat in data.get('stats', [])}
    # D&D Beyond stat order: 1=STR, 2=DEX, 3=CON, 4=INT, 5=WIS, 6=CHA
    stat_names = ['STR', 'DEX', 'CON', 'INT', 'WIS', 'CHA']
    stat_ids = [1, 2, 3, 4, 5, 6]
    stat_row = []
    for i in stat_ids:
        val = stats.get(i, 10)
        mod = (val - 10) // 2
        mod_str = f"+{mod}" if mod >= 0 else f"{mod}"
        stat_row.append(f"{val}({mod_str})")
    # Classes
    class_lines = []
    for c in classes:
        class_lines.append(f"<li>{c['definition']['name']} (Level {c['level']})</li>")
    class_lines_str = "\n".join(class_lines)
  
    # Languages (example, or fetch from data)
    languages = [
        "<li>Abyssal</li>",
        "<li>Common</li>",
        "<li>Infernal</li>",
        "<li>Thieves’ Cant</li>"
    ]
    # Senses (fetch from data if available)
    senses = []
    if 'senses' in data and isinstance(data['senses'], list):
        for sense in data['senses']:
            name = sense.get('name', '')
            value = sense.get('value', '')
            if name and value:
                senses.append(f"<li>{name}: {value}</li>")
    else:
        # fallback example
        senses = [
            "<li>Blindsight 10 ft.</li>",
            "<li>Darkvision 60 ft.</li>"
        ]
    # Backstory from notes
    backstory = ""
    notes = data.get('notes', {})
    if notes:
        backstory = notes.get('backstory', '') or ''
    # Markdown output
    lines = []
    lines.append(f"# {data.get('name', '')} ({'/'.join([c['definition']['name'] for c in classes])})\n")
    lines.append('  <table>')
    lines.append('    <tr>')
    lines.append(f'      <td colspan="1" valign="top"><img src="{avatar_url}" width="400"/></td>')
    lines.append('      <td colspan="2" valign="top">')
    lines.append('        <table valign="top">')
    lines.append('          <tr>')
    for n in stat_names:
        lines.append(f'            <th>{n}</th>')
    lines.append('          </tr>')
    lines.append('          <tr>')
    for v in stat_row:
        lines.append(f'            <td>{v}</td>')
    lines.append('          </tr>')
    lines.append('        </table>')
    lines.append('        <table>')
    lines.append('          <tr valign="top">')
    lines.append('            <td>')
    lines.append(f'              <strong>Player:</strong> {player}<br>')
    lines.append(f'              <strong>Race:</strong> {race}<br>')
    lines.append('              <strong>Class/Level:</strong>')
    lines.append('              <ul>')
    lines.append(class_lines_str)
    lines.append('              </ul>')
    lines.append('              <strong>Resistances:</strong>')
    lines.append('              <ul>')
    lines.append('                <!-- Add resistances here -->')
    lines.append('              </ul>')
    lines.append('            </td>')
    lines.append('            <td valign="top">')
    lines.append('              <ul>')
    lines.append('              </ul>')
    lines.append('              <strong>Languages:</strong>')
    lines.append('              <ul>')
    lines.extend(languages)
    lines.append('              </ul>')
    lines.append('              <strong>Senses</strong>')
    lines.append('              <ul>')
    lines.extend(senses)
    lines.append('              </ul>')
    lines.append('            </td>')
    lines.append('          </tr>')
    lines.append('        </table>')
    lines.append('      </td>')
    lines.append('    </tr>')
    lines.append('  </table>')
    lines.append('\n')
    lines.append('## Backstory \n')
    if backstory.strip():
        lines.append(backstory.strip() + "  \n")
    else:
        lines.append('Notes -> Backstory  \n')
    lines.append('---\n')
    lines.append('### D&DBeyond Link\n')
    lines.append(f'[Link to DNDB Character]({data.get("readonlyUrl", "")}) <-- output json data.readonlyUrl -->\n')
    lines.append(f'LastModifiedDate: <-- output json data.dateModified -->')
    return "\n".join(lines)

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(TEMP_DIR, exist_ok=True)
    os.makedirs(JSON_OUTPUT_DIR, exist_ok=True)
    characters = load_characters(CHARACTERS_YML)
    for char in characters:
        character_id = char.get('id') or char.get('characterId')
        if not character_id:
            continue
        character_data = fetch_character_json(character_id)
        if not character_data or not character_data.get('success'):
            print(f"Skipping character {character_id} due to fetch error.")
            continue
        # Optionally add player name from characters.yml
        character_data['data']['player'] = char.get('player', '')
        # Export character as {characterName}.json to JSON_OUTPUT_DIR
        character = character_data['data']
        character_name = character.get('name', f"character_{character_id}")
        safe_name = "".join(c for c in character_name if c.isalnum() or c in (' ', '_', '-')).rstrip()
        json_path = os.path.join(JSON_OUTPUT_DIR, f"{safe_name}.json")
        with open(json_path, "w") as jf:
            json.dump(character, jf, indent=2)
        print(f"Wrote {json_path}")
        md = render_markdown(character_data)
        out_path = os.path.join(OUTPUT_DIR, f"{character_id}.md")
        with open(out_path, "w") as f:
            f.write(md)
        print(f"Wrote {out_path}")

if __name__ == "__main__":
    main()