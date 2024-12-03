# process_handbook.py

import hashlib
import json
import os

def identify_handbook(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()
        if first_line.startswith("# Lunar Core") and "Handbook" in first_line:
            # Extract version
            handbook_version = first_line[len("# Lunar Core"):].strip()
            if handbook_version.endswith("Handbook"):
                handbook_version = handbook_version[:-len("Handbook")].strip()
            return 'LunarCore', handbook_version
        elif "Handbook generated in" in first_line:
            # Extract the date from first_line
            handbook_version = first_line[len("Handbook generated in"):].strip()
            return 'DanhengServer', handbook_version
        else:
            return None, None
    except Exception as e:
        return None, None

# Compute the hash of a file
def compute_file_hash(filename):
    hasher = hashlib.sha256()
    with open(filename, 'rb') as f:
        while True:
            data = f.read(65536)  # Read in 64KB chunks
            if not data:
                break
            hasher.update(data)
    return hasher.hexdigest()

class Item:
    def __init__(self, item_id, title, item_type, section, rarity=None, main_stats=None):
        self.id = item_id
        self.title = title
        self.type = item_type  # 'default', 'planars', 'base_material', 'lightcone', 'material', 'unknown', 'other', etc.
        self.section = section  # The section name from the Handbook
        self.rarity = rarity  # integer 2 to 5 or None
        self.main_stats = main_stats or []  # list of main stats, if applicable

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'type': self.type,
            'section': self.section,
            'rarity': self.rarity,
            'main_stats': self.main_stats
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            item_id=data['id'],
            title=data['title'],
            item_type=data['type'],
            section=data['section'],
            rarity=data.get('rarity'),
            main_stats=data.get('main_stats', [])
        )

class RogueBuffSu:
    def __init__(self, buff_id, name, category=None, buff_type=None, rarity=None):
        self.id = buff_id
        self.name = name
        self.category = category  # 'basic su', 'divergent su', 'equations', 'infinite blessings', 'resonance deployments', 'unknown'
        self.buff_type = buff_type  # 'Preservation', 'Memory', etc.
        self.rarity = rarity  # 'Mythic', 'Legendary', 'Rare', 'Common', or None

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'buff_type': self.buff_type,
            'rarity': self.rarity
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            buff_id=data['id'],
            name=data['name'],
            category=data.get('category'),
            buff_type=data.get('buff_type'),
            rarity=data.get('rarity')
        )

class HandbookData:
    def __init__(self):
        # Common sections
        self.avatars_list = []
        self.relics_list = []
        self.lightcones_list = []
        self.materials_list = []
        self.base_materials_list = []
        self.unknown_items_list = []
        self.other_items_list = []

        # LunarCore-specific sections
        self.props_list = []
        self.npc_monsters_list = []
        self.battle_stages = []
        self.battle_monsters_list = []
        self.mazes_list = []

        # DanhengServer-specific sections
        self.main_missions = []
        self.sub_missions = []
        self.rogue_buffs_su = []
        self.rogue_buffs_food = []
        self.rogue_buffs_various = []
        self.rogue_buffs_from_entities = []
        self.rogue_buffs_other = []
        self.rogue_buffs_unknown = []
        self.rogue_miracles = []

    def get_data(self):
        return self.__dict__

def process_handbook(filename, server_type, program_version=None):
    handbook_data = HandbookData()

    # Compute the hash of the input file
    file_hash = compute_file_hash(filename)

    # Define cache directory and files
    cache_dir = os.path.join('cache', server_type)
    cache_data_file = os.path.join(cache_dir, 'cache.json')
    cache_hash_file = os.path.join(cache_dir, 'hash.txt')
    cache_version_file = os.path.join(cache_dir, 'version.txt')

    # Check if cache exists and hashes and versions match
    cache_valid = False
    if (os.path.exists(cache_data_file) and os.path.exists(cache_hash_file)
            and os.path.exists(cache_version_file)):
        with open(cache_hash_file, 'r') as f:
            cached_hash = f.read().strip()
        with open(cache_version_file, 'r') as f:
            cached_version = f.read().strip()
        if cached_hash == file_hash and cached_version == (program_version or ''):
            cache_valid = True

    if cache_valid:
        # Load cache
        with open(cache_data_file, 'r', encoding='utf-8') as f:
            cache = json.load(f)
        # Reconstruct handbook_data
        for key, value in cache.items():
            if isinstance(value, list) and value and isinstance(value[0], dict):
                # For lists of dicts, we need to reconstruct objects
                if key in ['relics_list', 'lightcones_list', 'materials_list', 'base_materials_list',
                           'unknown_items_list', 'other_items_list']:
                    setattr(handbook_data, key, [Item.from_dict(item_dict) for item_dict in value])
                elif key == 'rogue_buffs_su':
                    setattr(handbook_data, key, [RogueBuffSu.from_dict(buff_dict) for buff_dict in value])
                else:
                    setattr(handbook_data, key, value)
            else:
                setattr(handbook_data, key, value)
        return handbook_data

    # Proceed to process the file as per server_type
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    if server_type == 'LunarCore':
        # Skip first line if it's a header
        if lines[0].startswith('# Lunar Core'):
            lines = lines[1:]

        current_section = None
        sections_to_skip = ['Lunar Core', 'Created', 'Commands']
        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # Check for section headers
            if line.startswith('# '):
                current_section = line[2:].strip()
                i += 1
                continue
            elif line == '':
                i += 1
                continue
            else:
                if current_section in sections_to_skip:
                    i += 1
                    continue

                # Process the line
                if ':' in line:
                    id_part, name_part = line.split(':', 1)
                else:
                    i += 1
                    continue

                id_str = id_part.strip()
                name = name_part.strip()

                # Now, depending on current_section, we store data accordingly
                if current_section == 'Avatars':
                    entry = {'id': id_str, 'name': name}
                    handbook_data.avatars_list.append(entry)
                elif current_section == 'Items':
                    process_item_line(id_str, name, handbook_data, current_section)
                elif current_section == 'Props (Spawnable)':
                    entry = {'id': id_str, 'name': name}
                    handbook_data.props_list.append(entry)
                elif current_section == 'NPC Monsters (Spawnable)':
                    entry = {'id': id_str, 'name': name}
                    handbook_data.npc_monsters_list.append(entry)
                elif current_section == 'Battle Stages':
                    entry = {'id': id_str, 'name': name}
                    handbook_data.battle_stages.append(entry)
                elif current_section == 'Battle Monsters':
                    entry = {'id': id_str, 'name': name}
                    handbook_data.battle_monsters_list.append(entry)
                elif current_section == 'Mazes':
                    entry = {'id': id_str, 'name': name}
                    handbook_data.mazes_list.append(entry)
                else:
                    pass  # Skip other sections

                i += 1

    elif server_type == 'DanhengServer':
        # Skip the first line "Handbook generated in {date} {time}"
        lines = lines[1:]

        current_section = None
        sections_to_skip = ['Command']
        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # Check for section headers
            if line.startswith('#'):
                current_section = line[1:].strip()
                i += 1
                continue
            elif line == '':
                i += 1
                continue
            else:
                if current_section in sections_to_skip:
                    i += 1
                    continue

                # Process the line
                if ':' in line:
                    id_part, name_part = line.split(':', 1)
                else:
                    i += 1
                    continue

                id_str = id_part.strip()
                name = name_part.strip()

                if current_section == 'Avatar':
                    entry = {'id': id_str, 'name': name}
                    handbook_data.avatars_list.append(entry)
                elif current_section == 'Item':
                    process_item_line(id_str, name, handbook_data, current_section)
                elif current_section == 'MainMission':
                    entry = {'id': id_str, 'name': name}
                    handbook_data.main_missions.append(entry)
                elif current_section == 'SubMission':
                    entry = {'id': id_str, 'name': name}
                    handbook_data.sub_missions.append(entry)
                elif current_section == 'RogueBuff':
                    process_rogue_buff_line(id_str, name, handbook_data)
                elif current_section == 'RogueMiracle':
                    entry = {'id': id_str, 'name': name}
                    handbook_data.rogue_miracles.append(entry)
                else:
                    pass  # Skip other sections

                i += 1

    # Prepare the cache data
    cache = {}
    for key, value in handbook_data.get_data().items():
        if isinstance(value, list) and value and isinstance(value[0], (Item, RogueBuffSu)):
            cache[key] = [obj.to_dict() for obj in value]
        else:
            cache[key] = value

    # Ensure the cache directory exists
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)

    # Save the cache data
    with open(cache_data_file, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=4)

    # Save the file hash
    with open(cache_hash_file, 'w') as f:
        f.write(file_hash)

    # Save the program version
    with open(cache_version_file, 'w') as f:
        f.write(program_version or '')

    # Return the HandbookData object
    return handbook_data

def process_item_line(id_str, name, handbook_data, current_section):
    # Skip IDs where the id is not a number
    if not id_str.isdigit():
        return

    id_int = int(id_str)

    # Assign item_type based on given rules
    item_type = None

    # First, check for 'unknown' items (name contains 'null')
    if 'null' in name.lower():
        item_type = 'unknown'
    # Characters in items. Skipping.
    elif 1001 <= id_int <= 8100:
        return
    # Materials: IDs in range 110000 - 119999
    elif 110000 <= id_int <= 119999:
        item_type = 'material'
    # Base materials: IDs 1 - 1000
    elif 1 <= id_int <= 1000:
        item_type = 'base_material'
    # Lightcones: IDs 20000 - 30000
    elif 20000 <= id_int <= 30000:
        item_type = 'lightcone'
        # Determine rarity based on the second digit
        if len(id_str) < 2:
            return  # Invalid ID format
        second_digit = int(id_str[1])
        if second_digit == 0:
            rarity = 3
        elif second_digit in [1, 2]:
            rarity = 4
        elif second_digit == 3:
            rarity = 5
        elif second_digit == 4:
            rarity = 'free'
        else:
            rarity = None  # Unknown rarity
        item = Item(item_id=id_str, title=name, item_type=item_type, section=current_section, rarity=rarity)
        handbook_data.lightcones_list.append(item)
        return
    # Relics (default and planars)
    elif len(id_str) == 5 and id_str[1] != '0':
        first_digit = int(id_str[0])
        if 3 <= first_digit <= 6:
            # Determine the rarity based on the first digit minus 1
            rarity = first_digit - 1  # Rarity from 2 to 5

            # Determine the type based on the last digit
            last_digit = int(id_str[-1])
            if last_digit in [1, 2, 3, 4]:
                item_type = 'default'
            elif last_digit in [5, 6]:
                item_type = 'planars'
            else:
                item_type = 'unknown'  # Could be other types in future

            # Create the Item object
            item = Item(item_id=id_str, title=name, item_type=item_type, section=current_section, rarity=rarity)
            # Add to relics_list
            handbook_data.relics_list.append(item)
            return
        else:
            # IDs that don't meet the criteria fall into 'other'
            item_type = 'other'
    else:
        # IDs that don't meet any of the above criteria are 'other'
        item_type = 'other'

    # Create the Item object
    item = Item(item_id=id_str, title=name, item_type=item_type, section=current_section)
    # Depending on item_type, store in appropriate list
    if item_type == 'material':
        handbook_data.materials_list.append(item)
    elif item_type == 'base_material':
        handbook_data.base_materials_list.append(item)
    elif item_type == 'unknown':
        handbook_data.unknown_items_list.append(item)
    elif item_type == 'other':
        handbook_data.other_items_list.append(item)
    else:
        pass

def process_rogue_buff_line(id_str, name, handbook_data):
    # Sift out the empty
    if name.startswith("[") or name.startswith("0 ---"):
        entry = {'id': id_str, 'name': name}
        handbook_data.rogue_buffs_unknown.append(entry)
    # Su buffs
    elif len(id_str) == 8 and id_str.startswith("6"):
        # Create RogueBuffSu object
        buff_id = id_str
        buff_name = name

        # Determine category based on the first digits
        if buff_id.startswith('612'):
            category = 'basic su'
        elif buff_id.startswith('615'):
            category = 'divergent su'
        elif buff_id.startswith('67'):
            category = 'equations'
        elif buff_id.startswith('620'):
            category = 'infinite blessings'
        elif buff_id.startswith('650'):
            category = 'resonance deployments'
        else:
            category = 'unknown'

        buff_type = None
        rarity = None

        # For 'basic su' and 'divergent su' categories, determine type and rarity
        if category in ['basic su', 'divergent su']:
            fourth_digit = buff_id[3]  # fourth digit (index 3)
            fifth_digit = buff_id[4]  # fifth digit (index 4)

            # Map the fourth digit to buff_type
            type_map = {
                '0': 'Preservation',
                '1': 'Memory',
                '2': 'Nonexistence',
                '3': 'Abundance',
                '4': 'Hunting',
                '5': 'Destruction',
                '6': 'Joy',
                '7': 'Spreading',
                '8': 'Erudition'
            }
            buff_type = type_map.get(fourth_digit, 'Unknown')

            # Map the fifth digit to rarity
            rarity_map = {
                '2': 'Mythic',
                '3': 'Legendary',
                '4': 'Rare',
                '5': 'Common'
            }
            rarity = rarity_map.get(fifth_digit, None)
        else:
            pass  # For other categories, we might not have buff_type and rarity

        rogue_buff = RogueBuffSu(buff_id=buff_id, name=buff_name, category=category, buff_type=buff_type, rarity=rarity)
        handbook_data.rogue_buffs_su.append(rogue_buff)
    # Food
    elif len(id_str) == 8 and id_str.startswith("40"):
        entry = {'id': id_str, 'name': name}
        handbook_data.rogue_buffs_food.append(entry)
    # Various buffs
    elif len(id_str) == 9 and id_str.startswith("3"):
        entry = {'id': id_str, 'name': name}
        handbook_data.rogue_buffs_various.append(entry)
    elif len(id_str) == 8 and (id_str.startswith('1') or id_str.startswith('8')):
        entry = {'id': id_str, 'name': name}
        handbook_data.rogue_buffs_from_entities.append(entry)
    else:
        entry = {'id': id_str, 'name': name}
        handbook_data.rogue_buffs_other.append(entry)
