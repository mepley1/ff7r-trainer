# Constants
BASE_OFFSET = 0xB6D80
CHARACTER_OFFSET = 0x3E60

# Base Character Offsets Class
class CharacterOffsets:
    def __init__(self, hp, max_hp, mp, max_mp, atb, atb_slots, limit, luck, p_def, m_def, p_atk, m_atk, exp, in_party, strength=None, magic=None):
        self.hp = [BASE_OFFSET, CHARACTER_OFFSET, hp]
        self.max_hp = [BASE_OFFSET, CHARACTER_OFFSET, max_hp]
        self.mp = [BASE_OFFSET, CHARACTER_OFFSET, mp]
        self.max_mp = [BASE_OFFSET, CHARACTER_OFFSET, max_mp]
        self.atb = [BASE_OFFSET, CHARACTER_OFFSET, atb]
        self.atb_slots = [BASE_OFFSET, CHARACTER_OFFSET, atb_slots]
        self.limit = [BASE_OFFSET, CHARACTER_OFFSET, limit]
        self.luck = [BASE_OFFSET, CHARACTER_OFFSET, luck]
        self.p_def = [BASE_OFFSET, CHARACTER_OFFSET, p_def]
        self.m_def = [BASE_OFFSET, CHARACTER_OFFSET, m_def]
        self.p_atk = [BASE_OFFSET, CHARACTER_OFFSET, p_atk]
        self.m_atk = [BASE_OFFSET, CHARACTER_OFFSET, m_atk]
        self.exp = [BASE_OFFSET, CHARACTER_OFFSET, exp]
        self.in_party = [BASE_OFFSET, CHARACTER_OFFSET, in_party]
        self.strength = [BASE_OFFSET, CHARACTER_OFFSET, strength] if strength else None
        self.magic = [BASE_OFFSET, CHARACTER_OFFSET, magic] if magic else None

# Character Offsets
class Offsets:
    Aerith = CharacterOffsets(hp=0xF0, max_hp=0xF4, mp=0xF8, max_mp=0xFC, atb=0x104, atb_slots=0xE2, limit=0xE4, luck=0x118, p_def=0x110, m_def=0x114, p_atk=0x108, m_atk=0x10C, exp=0x100, in_party=0x5001F)
    Barret = CharacterOffsets(hp=0x70, max_hp=0x74, mp=0x78, max_mp=0x7C, atb=0x84, atb_slots=0x62, limit=0x64, luck=0x98, p_def=0x90, m_def=0x94, p_atk=0x88, m_atk=0x8C, exp=0x80, in_party=0x5001D)
    Cloud = CharacterOffsets(hp=0x30, max_hp=0x34, mp=0x38, max_mp=0x3C, atb=0x44, atb_slots=0x22, limit=0x24, luck=0x58, p_def=0x50, m_def=0x54, p_atk=0x48, m_atk=0x4C, exp=0x40, in_party=0x5001C, strength=0x220, magic=0x224)
    Red = CharacterOffsets(hp=0x130, max_hp=0x134, mp=0x138, max_mp=0x13C, atb=0x144, atb_slots=None, limit=None, luck=0x158, p_def=0x150, m_def=0x154, p_atk=0x148, m_atk=0x14C, exp=0x140, in_party=0x50020)
    Sonon = CharacterOffsets(hp=0x1B0, max_hp=0x1B4, mp=0x1B8, max_mp=0x1BC, atb=0x1C4, atb_slots=0x1A2, limit=0x1A4, luck=0x1D8, p_def=0x1D0, m_def=0x1D4, p_atk=0x1C8, m_atk=0x1CC, exp=0x1C0, in_party=0x50022)
    Tifa = CharacterOffsets(hp=0xB0, max_hp=0xB4, mp=0xB8, max_mp=0xBC, atb=0xC4, atb_slots=0xA2, limit=0xA4, luck=0xD8, p_def=0xD0, m_def=0xD4, p_atk=0xC8, m_atk=0xCC, exp=0xC0, in_party=0x5001E)
    Yuffie = CharacterOffsets(hp=0x170, max_hp=0x174, mp=0x178, max_mp=0x17C, atb=0x184, atb_slots=0x162, limit=0x164, luck=0x198, p_def=0x190, m_def=0x194, p_atk=0x188, m_atk=0x18C, exp=0x180, in_party=0x50021)

    # Meta Offsets
    Meta = {
        'player_atb_rate': [0x38, 0x719C],
        'ai_atb_rate': [0x38, 0x751C],
        'atb_per_slot': [0x38, 0x7010],
        'hard_mode_ap_multiplier': [0x38, 0x93F0],
        'hard_mode_exp_multiplier': [0x38, 0x93B8],
        'controlled_char': [BASE_OFFSET, CHARACTER_OFFSET, 0x5001B],
        'hard_mode': [BASE_OFFSET, CHARACTER_OFFSET, 0x42F79],
        'play_time': [BASE_OFFSET, CHARACTER_OFFSET, 0x2A0],
    }

    # Item Offsets
    item_offsets = {
        'Money': {'Gil': [0x356C4], 'Moogle Medals': [0x3570C]},
        'Healing': {
            'Potion': [0x35664], 'Hi Potion': [0x3573C], 'Mega Potion': [0x35A84],
            'Elixir': [0x35844], 'Ether': [0x3567C], 'Turbo Ether': [0x35C7C],
            'Remedy': [0x35B14], 'Phoenix Down': [0x356F4], 'Maiden\'s Kiss': [0x3582C],
            'Adrenaline': [0x35814], 'Smelling Salts': [0x359C4], 'Echo Mist': [0x35A54], 'Celeris': [0x35C4C],
        },
        'Offensive': {
            'Attacks': {
                'Mr. Cuddlesworth': [0x35D9C], 'Molotov Cocktail': [0x35E44], 
                'Grenade': [0x356DC], 'Big Bomber': [0x35AB4], 'Orb of Gravity': [0x35874]
            },
            'Status Effects': {'Hazardous Material': [0x359DC], 'Spider Web': [0x359F4]}
        },
        'Misc': {'Yellow Flower': [0x35724], 'Combat Analyzer': [0x357E4]}
    }
