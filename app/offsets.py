""" All pointers are contained in this file. """

class Offsets:
    """ All memory offsets. """

    Aerith = {
        'hp': [0xB6D80, 0x3E60, 0xF0], # ushort
        'max_hp': [0xB6D80, 0x3E60, 0xF4],
        'mp': [0xB6D80, 0x3E60, 0xF8],
        'max_mp': [0xB6D80, 0x3E60, 0xFC],
        'atb': [0xB6D80, 0x3E60, 0x104],
        'atb_slots': [0xB6D80, 0x3E60, 0xE2],
        'limit': [0xB6D80, 0x3E60, 0xE4],
        'luck': [0xB6D80, 0x3E60, 0x118],
        #'strength': 
        #'magic':
        'p_def': [0xB6D80, 0x3E60, 0x110],
        'm_def': [0xB6D80, 0x3E60, 0x114],
        'p_atk': [0xB6D80, 0x3E60, 0x108],
        'm_atk': [0xB6D80, 0x3E60, 0x10C],
        'exp': [0xB6D80, 0x3E60, 0x100],
        'in_party': [0xb6d80, 0x3e60, 0x5001f],
    }

    Barret = {
        'hp': [0xB6D80, 0x3E60, 0x70],
        'max_hp': [0xB6D80, 0x3E60, 0x74],
        'mp': [0xB6D80, 0x3E60, 0x78],
        'max_mp': [0xB6D80, 0x3E60, 0x7C],
        'atb': [0xB6D80, 0x3E60, 0x84], # float
        'atb_slots': [0xB6D80, 0x3E60, 0x62], # byte
        'limit': [0xB6D80, 0x3E60, 0x64], # float
        'luck': [0xB6D80, 0x3E60, 0x98],
        #'strength': 
        #'magic':
        'p_def': [0xB6D80, 0x3E60, 0x90],
        'm_def': [0xB6D80, 0x3E60, 0x94],
        'p_atk': [0xB6D80, 0x3E60, 0x88],
        'm_atk': [0xB6D80, 0x3E60, 0x8C],
        'exp': [0xB6D80, 0x3E60, 0x80], # uint
        'in_party': [0xb6d80, 0x3e60, 0x5001d], # byte
    }

    Cloud = {
        'hp': [0xB6D80, 0x3E60, 0x30],
        'max_hp': [0xB6D80, 0x3E60, 0x34],
        'mp': [0xB6D80, 0x3E60, 0x38],
        'max_mp': [0xB6D80, 0x3E60, 0x3C],
        'atb': [0xB6D80, 0x3E60, 0x44],  # float
        'atb_slots': [0xB6D80, 0x3E60, 0x22],
        'limit': [0xB6D80, 0x3E60, 0x24],  # float
        'luck': [0xB6D80, 0x3E60, 0x58],
        'strength': [0xB6D80, 0x3E60, 0x220],  # byte
        'magic': [0xB6D80, 0x3E60, 0x224],  # byte
        'p_def': [0xB6D80, 0x3E60, 0x50],  # byte
        'm_def': [0xB6D80, 0x3E60, 0x54],  # byte
        'p_atk': [0xB6D80, 0x3E60, 0x48],
        'm_atk': [0xB6D80, 0x3E60, 0x4C],
        'exp': [0xB6D80, 0x3E60, 0x40],  # 4 bytes
        'in_party': [0xb6d80, 0x3e60, 0x5001c],
    }

    Red = {
        'hp': [0xB6D80, 0x3E60, 0x130],
        'max_hp': [0xB6D80, 0x3E60, 0x134],
        'mp': [0xB6D80, 0x3E60, 0x138],
        'max_mp': [0xB6D80, 0x3E60, 0x13C],
        'atb': [0xB6D80, 0x3E60, 0x144],
        #'atb_slots':
        #'limit':
        'luck': [0xB6D80, 0x3E60, 0x158],
        #'strength':
        #'magic':
        'p_def': [0xB6D80, 0x3E60, 0x150],
        'm_def': [0xB6D80, 0x3E60, 0x154],
        'p_atk': [0xB6D80, 0x3E60, 0x148],
        'm_atk': [0xB6D80, 0x3E60, 0x14C],
        'exp': [0xB6D80, 0x3E60, 0x140],
        'in_party': [0xb6d80, 0x3e60, 0x50020],
    }

    Sonon = {
        'hp': [0xB6D80, 0x3E60, 0x1B0],
        'max_hp': [0xB6D80, 0x3E60, 0x1B4],
        'mp': [0xB6D80, 0x3E60, 0x1B8],
        'max_mp': [0xB6D80, 0x3E60, 0x1BC],
        'atb': [0xB6D80, 0x3E60, 0x1C4], # float
        'atb_slots': [0xB6D80, 0x3E60, 0x1A2], # guess??
        'limit': [0xB6D80, 0x3E60, 0x1A4],
        'luck': [0xB6D80, 0x3E60, 0x1D8],
        #'strength': 
        #'magic':
        'p_def': [0xB6D80, 0x3E60, 0x1D0],
        'm_def': [0xB6D80, 0x3E60, 0x1D4],
        'p_atk': [0xB6D80, 0x3E60, 0x1C8],
        'm_atk': [0xB6D80, 0x3E60, 0x1CC],
        'exp': [0xB6D80, 0x3E60, 0x1C0],
        'in_party': [0xb6d80, 0x3e60, 0x50022],
    }

    Tifa = {
        'hp': [0xB6D80, 0x3E60, 0xB0],
        'max_hp': [0xB6D80, 0x3E60, 0xB4],
        'mp': [0xB6D80, 0x3E60, 0xB8],
        'max_mp': [0xB6D80, 0x3E60, 0xBC],
        'atb': [0xB6D80, 0x3E60, 0xC4], # float
        'atb_slots': [0xB6D80, 0x3E60, 0xA2], # 1 byte
        'limit': [0xB6D80, 0x3E60, 0xA4], # float
        'luck': [0xB6D80, 0x3E60, 0xD8],
        #'strength': 
        #'magic':
        'p_def': [0xB6D80, 0x3E60, 0xD0],
        'm_def': [0xB6D80, 0x3E60, 0xD4],
        'p_atk': [0xB6D80, 0x3E60, 0xC8],
        'm_atk': [0xB6D80, 0x3E60, 0xCC],
        'exp': [0xB6D80, 0x3E60, 0xC0],
        'in_party': [0xb6d80, 0x3e60, 0x5001e],
    }

    Yuffie = {
        'hp': [0xB6D80, 0x3E60, 0x170],
        'max_hp': [0xB6D80, 0x3E60, 0x174],
        'mp': [0xB6D80, 0x3E60, 0x178],
        'max_mp': [0xB6D80, 0x3E60, 0x17C],
        'atb': [0xB6D80, 0x3E60, 0x184], # float
        'atb_slots': [0xB6D80, 0x3E60, 0x162], # guess???
        'limit': [0xB6D80, 0x3E60, 0x164], # guess???
        'luck': [0xB6D80, 0x3E60, 0x198],
        #'strength': 
        #'magic':
        'p_def': [0xB6D80, 0x3E60, 0x190],
        'm_def': [0xB6D80, 0x3E60, 0x194],
        'p_atk': [0xB6D80, 0x3E60, 0x188],
        'm_atk': [0xB6D80, 0x3E60, 0x18C],
        'exp': [0xB6D80, 0x3E60, 0x180],
        'in_party': [0xb6d80, 0x3e60, 0x50021],
    }


    ### Meta
    Meta = {
        # From data_base:
        'player_atb_rate': [0x38, 0x719C], # data_base, float (normal = 1)
        'ai_atb_rate': [0x38, 0x751C], # data_base, float (normal = 0.349999994)
        'atb_per_slot': [0x38, 0x7010], # 4 bytes
        'hard_mode_ap_multiplier': [0x38, 0x93F0], # 300
        'hard_mode_exp_multiplier': [0x38, 0x93B8], # 200
        # From player_base:
        'controlled_char': [0xB6D80, 0x3E60, 0x5001B],
        'hard_mode': [0xB6D80, 0x3E60, 0x42F79], # 2 bytes
        'play_time': [0xB6D80, 0x3E60, 0x2A0], # 4 bytes uint
    }


    ### Inventory items, offset from player_base
    item_offsets = {

        # Money etc
        '-- MONEY --': None, # Label for the OptionMenu
        'Gil': [0x356C4],
        'Moogle Medals': [0x3570C],

        # Healing
        '-- HEALING --': None, # Label for the OptionMenu
        'Potion': [0x35664],
        'Hi Potion': [0x3573C],
        'Mega Potion': [0x35A84],
        'Elixir': [0x35844],
        'Ether': [0x3567C],
        'Turbo Ether': [0x35C7C],
        'Remedy': [0x35B14],
        'Phoenix Down': [0x356F4],
        'Maiden\'s Kiss': [0x3582C],
        'Adrenaline': [0x35814],
        'Smelling Salts': [0x359C4],
        'Echo Mist': [0x35A54],
        'Celeris': [0x35C4C],

        # Offensive items - attacks
        '-- OFFENSE / DMG --': None, # Label for the OptionMenu
        'Mr. Cuddlesworth': [0x35D9C],
        'Molotov Cocktail': [0x35E44],
        'Grenade': [0x356DC],
        'Big Bomber': [0x35AB4],
        'Orb of Gravity': [0x35874],

        # Offensive items - status effects
        '-- OFFENSE / STATUS --': None, # Label for the OptionMenu
        'Hazardous Material': [0x359DC],
        'Spider Web': [0x359F4],

        # Misc
        '-- MISC --': None, # Label for the OptionMenu
        'Yellow Flower': [0x35724],
        'Combat Analyzer': [0x357E4],
    }
