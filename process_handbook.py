import hashlib
import json
import os

# === Конфигурация параметров сортировки ===

# Параметры для обработки разделов в зависимости от типа сервера
SECTION_CONFIG = {
    'LunarCore': {
        'skip_sections': ['Lunar Core', 'Created', 'Commands'],
        'processors': {
            'Avatars': lambda id_str, name, hd, section: hd.avatars_list.append({'id': id_str, 'name': name}),
            'Items': lambda id_str, name, hd, section: process_item_line(id_str, name, hd, section),
            'Props (Spawnable)': lambda id_str, name, hd, section: hd.props_list.append({'id': id_str, 'name': name}),
            'NPC Monsters (Spawnable)': lambda id_str, name, hd, section: hd.npc_monsters_list.append({'id': id_str, 'name': name}),
            'Battle Stages': lambda id_str, name, hd, section: hd.battle_stages.append({'id': id_str, 'name': name}),
            'Battle Monsters': lambda id_str, name, hd, section: hd.battle_monsters_list.append({'id': id_str, 'name': name}),
            'Mazes': lambda id_str, name, hd, section: hd.mazes_list.append({'id': id_str, 'name': name}),
        }
    },
    'DanhengServer': {
        'skip_sections': ['Command'],
        'processors': {
            'Avatar': lambda id_str, name, hd, section: hd.avatars_list.append({'id': id_str, 'name': name}),
            'Item': lambda id_str, name, hd, section: process_item_line(id_str, name, hd, section),
            'MainMission': lambda id_str, name, hd, section: hd.main_missions.append({'id': id_str, 'name': name}),
            'SubMission': lambda id_str, name, hd, section: hd.sub_missions.append({'id': id_str, 'name': name}),
            'RogueBuff': lambda id_str, name, hd, section: process_rogue_buff_line(id_str, name, hd),
            'RogueMiracle': lambda id_str, name, hd, section: hd.rogue_miracles.append({'id': id_str, 'name': name}),
        }
    }
}

# Параметры для сортировки предметов
ITEM_SORTING_CONFIG = {
    'unknown_marker': 'null',
    'skip_range': (1001, 8100),
    'material_range': (110000, 119999),
    'base_material_range': (1, 1000),
    'lightcone_range': (20000, 30000),
    'lightcone_rarity_map': {
        '0': 3,
        '1': 4,
        '2': 4,
        '3': 5,
        '4': 'free'
    },
    'relic_valid_length': 5,
    'relic_valid_first_digit_range': (3, 6),
    'relic_type_map': {
        'default': [1, 2, 3, 4],
        'planars': [5, 6]
    }
}

# Параметры для обработки баффов RogueBuff
ROGUE_BUFF_CONFIG = {
    'empty_prefixes': ['[', '0 ---'],
    'su': {
        'id_length': 8,
        'prefix': '6',
        'category_map': {
            '612': 'basic su',
            '615': 'divergent su',
            '616': 'divergent su: PH',
            '67': 'equations',
            '63': 'Golden Blood',
            '620': 'infinite blessings',
            '650': 'resonance deployments'
        },
        'type_map': {
            '0': 'Preservation',
            '1': 'Remembrance',
            '2': 'Nihility',
            '3': 'Abundance',
            '4': 'The Hunt',
            '5': 'Destruction',
            '6': 'Elation',
            '7': 'Propagation',
            '8': 'Erudition',
            "9": 'Harmony'
        },
        'rarity_map': {
            '2': 'Mythic',
            '3': 'Legendary',
            '4': 'Rare',
            '5': 'Common'
        }
    },
    'food': {
        'prefix': '40',
        'id_length': 8
    },
    'various': {
        'prefix': '3',
        'id_length': 9
    },
    'from_entities': {
        'prefixes': ['1', '8'],
        'id_length': 8
    }
}

# === Классы данных ===

class Item:
    def __init__(self, item_id, title, item_type, section, rarity=None, main_stats=None):
        self.id = item_id
        self.title = title
        self.type = item_type  # 'default', 'planars', 'base_material', 'lightcone', 'material', 'unknown', 'other'
        self.section = section
        self.rarity = rarity
        self.main_stats = main_stats or []

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
        self.category = category  # например, 'basic su', 'divergent su', 'equations', и т.д.
        self.buff_type = buff_type  # например, 'Preservation', 'Memory', и т.д.
        self.rarity = rarity  # 'Mythic', 'Legendary', 'Rare', 'Common' или None

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
        # Общие разделы
        self.avatars_list = []
        self.relics_list = []
        self.lightcones_list = []
        self.materials_list = []
        self.base_materials_list = []
        self.unknown_items_list = []
        self.other_items_list = []
        # Только для LunarCore
        self.props_list = []
        self.npc_monsters_list = []
        self.battle_stages = []
        self.battle_monsters_list = []
        self.mazes_list = []
        # Только для DanhengServer
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

# === Вспомогательные функции ===

def identify_handbook(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()
        if first_line.startswith("# Lunar Core") and "Handbook" in first_line:
            handbook_version = first_line[len("# Lunar Core"):].strip()
            if handbook_version.endswith("Handbook"):
                handbook_version = handbook_version[:-len("Handbook")].strip()
            return 'LunarCore', handbook_version
        elif "Handbook generated in" in first_line:
            handbook_version = first_line[len("Handbook generated in"):].strip()
            return 'DanhengServer', handbook_version
        else:
            return None, None
    except Exception:
        return None, None

def compute_file_hash(filename):
    hasher = hashlib.sha256()
    with open(filename, 'rb') as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()

# === Основные функции обработки строк ===

def process_item_line(id_str, name, handbook_data, current_section):
    # Если ID не является числом, пропускаем
    if not id_str.isdigit():
        return

    id_int = int(id_str)

    # Если название содержит маркер "null", считаем предмет неизвестным
    if ITEM_SORTING_CONFIG['unknown_marker'] in name.lower():
        item_type = 'unknown'
    # Пропускаем диапазон, относящийся к персонажам
    elif ITEM_SORTING_CONFIG['skip_range'][0] <= id_int <= ITEM_SORTING_CONFIG['skip_range'][1]:
        return
    elif ITEM_SORTING_CONFIG['material_range'][0] <= id_int <= ITEM_SORTING_CONFIG['material_range'][1]:
        item_type = 'material'
    elif ITEM_SORTING_CONFIG['base_material_range'][0] <= id_int <= ITEM_SORTING_CONFIG['base_material_range'][1]:
        item_type = 'base_material'
    elif ITEM_SORTING_CONFIG['lightcone_range'][0] <= id_int <= ITEM_SORTING_CONFIG['lightcone_range'][1]:
        item_type = 'lightcone'
        # Определяем редкость по второй цифре
        if len(id_str) < 2:
            return
        second_digit = id_str[1]
        rarity = ITEM_SORTING_CONFIG['lightcone_rarity_map'].get(second_digit)
        item = Item(item_id=id_str, title=name, item_type=item_type, section=current_section, rarity=rarity)
        handbook_data.lightcones_list.append(item)
        return
    # Обработка реликвий
    elif len(id_str) == ITEM_SORTING_CONFIG['relic_valid_length'] and id_str[1] != '0':
        first_digit = int(id_str[0])
        low, high = ITEM_SORTING_CONFIG['relic_valid_first_digit_range']
        if low <= first_digit <= high:
            rarity = first_digit - 1  # Редкость от 2 до 5
            last_digit = int(id_str[-1])
            if last_digit in ITEM_SORTING_CONFIG['relic_type_map']['default']:
                item_type = 'default'
            elif last_digit in ITEM_SORTING_CONFIG['relic_type_map']['planars']:
                item_type = 'planars'
            else:
                item_type = 'unknown'
            item = Item(item_id=id_str, title=name, item_type=item_type, section=current_section, rarity=rarity)
            handbook_data.relics_list.append(item)
            return
        else:
            item_type = 'other'
    else:
        item_type = 'other'

    # Создаём объект Item и распределяем по спискам
    item = Item(item_id=id_str, title=name, item_type=item_type, section=current_section)
    if item_type == 'material':
        handbook_data.materials_list.append(item)
    elif item_type == 'base_material':
        handbook_data.base_materials_list.append(item)
    elif item_type == 'unknown':
        handbook_data.unknown_items_list.append(item)
    elif item_type == 'other':
        handbook_data.other_items_list.append(item)

def process_rogue_buff_line(id_str, name, handbook_data):
    # Если название начинается с указанных префиксов, считаем бафф неизвестным
    if any(name.startswith(prefix) for prefix in ROGUE_BUFF_CONFIG['empty_prefixes']):
        handbook_data.rogue_buffs_unknown.append({'id': id_str, 'name': name})
    # Обработка SU баффов
    elif len(id_str) == ROGUE_BUFF_CONFIG['su']['id_length'] and id_str.startswith(ROGUE_BUFF_CONFIG['su']['prefix']):
        buff_id = id_str
        buff_name = name
        # Определяем категорию по префиксу
        category = 'unknown'
        for key, cat in ROGUE_BUFF_CONFIG['su']['category_map'].items():
            if id_str.startswith(key):
                category = cat
                break

        buff_type = None
        rarity = None
        if category in ['basic su', 'divergent su', 'divergent su: PH']:
            # Четвертая цифра определяет тип
            fourth_digit = id_str[3]
            buff_type = ROGUE_BUFF_CONFIG['su']['type_map'].get(fourth_digit, 'Unknown')
            # Пятая цифра определяет редкость
            fifth_digit = id_str[4]
            rarity = ROGUE_BUFF_CONFIG['su']['rarity_map'].get(fifth_digit)
        rogue_buff = RogueBuffSu(buff_id=buff_id, name=buff_name, category=category, buff_type=buff_type, rarity=rarity)
        handbook_data.rogue_buffs_su.append(rogue_buff)
    # Баффы еды
    elif len(id_str) == ROGUE_BUFF_CONFIG['food']['id_length'] and id_str.startswith(ROGUE_BUFF_CONFIG['food']['prefix']):
        handbook_data.rogue_buffs_food.append({'id': id_str, 'name': name})
    # Различные баффы
    elif len(id_str) == ROGUE_BUFF_CONFIG['various']['id_length'] and id_str.startswith(ROGUE_BUFF_CONFIG['various']['prefix']):
        handbook_data.rogue_buffs_various.append({'id': id_str, 'name': name})
    # Баффы от сущностей
    elif len(id_str) == ROGUE_BUFF_CONFIG['from_entities']['id_length'] and any(id_str.startswith(pref) for pref in ROGUE_BUFF_CONFIG['from_entities']['prefixes']):
        handbook_data.rogue_buffs_from_entities.append({'id': id_str, 'name': name})
    else:
        handbook_data.rogue_buffs_other.append({'id': id_str, 'name': name})

# === Основная функция обработки справочника ===

def process_handbook(filename, server_type, program_version=None):
    handbook_data = HandbookData()
    file_hash = compute_file_hash(filename)

    # Определяем директорию и файлы кэша
    cache_dir = os.path.join('cache', server_type)
    cache_data_file = os.path.join(cache_dir, 'cache.json')
    cache_hash_file = os.path.join(cache_dir, 'hash.txt')
    cache_version_file = os.path.join(cache_dir, 'version.txt')

    # Проверка валидности кэша
    cache_valid = False
    if os.path.exists(cache_data_file) and os.path.exists(cache_hash_file) and os.path.exists(cache_version_file):
        with open(cache_hash_file, 'r') as f:
            cached_hash = f.read().strip()
        with open(cache_version_file, 'r') as f:
            cached_version = f.read().strip()
        if program_version != "beta" and cached_hash == file_hash and cached_version == (program_version or ''):
            cache_valid = True

    if cache_valid:
        with open(cache_data_file, 'r', encoding='utf-8') as f:
            cache = json.load(f)
        # Восстанавливаем данные справочника
        for key, value in cache.items():
            if isinstance(value, list) and value and isinstance(value[0], dict):
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

    # Чтение файла и подготовка строк
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Обработка заголовка в зависимости от типа сервера
    if server_type == 'LunarCore':
        if lines[0].startswith('# Lunar Core'):
            lines = lines[1:]
    elif server_type == 'DanhengServer':
        lines = lines[1:]

    config = SECTION_CONFIG.get(server_type, {})
    skip_sections = config.get('skip_sections', [])
    processors = config.get('processors', {})

    current_section = None
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        # Если строка – заголовок раздела
        if line.startswith('#'):
            # Для LunarCore заголовок начинается с "# ", для DanhengServer – с "#"
            current_section = line.lstrip('#').strip()
            i += 1
            continue
        # Пропускаем разделы, указанные в конфигурации
        if current_section in skip_sections:
            i += 1
            continue
        # Обрабатываем строку с раздела, если она содержит ":"
        if ':' in line:
            id_part, name_part = line.split(':', 1)
            id_str = id_part.strip()
            name = name_part.strip()
            # Если для текущего раздела определён обработчик, вызываем его
            if current_section in processors:
                processors[current_section](id_str, name, handbook_data, current_section)
        i += 1

    # Кэширование результатов
    cache = {}
    for key, value in handbook_data.get_data().items():
        if isinstance(value, list) and value and isinstance(value[0], (Item, RogueBuffSu)):
            cache[key] = [obj.to_dict() for obj in value]
        else:
            cache[key] = value

    os.makedirs(cache_dir, exist_ok=True)
    with open(cache_data_file, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=4)
    with open(cache_hash_file, 'w') as f:
        f.write(file_hash)
    with open(cache_version_file, 'w') as f:
        f.write(program_version or '')

    return handbook_data
