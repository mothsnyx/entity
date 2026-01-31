# emojis.py - Custom Discord Emojis Configuration
# 
# HOW TO USE:
# 1. Upload your emojis to Discord Server (Server Settings → Emoji)
# 2. In Discord, type \:emoji_name: to get the full emoji code
# 3. Replace the placeholder IDs below with your actual emoji IDs
# 4. Import in main.py: from emojis import *

# ===================================
# CURRENCY EMOJIS
# ===================================
# Get emoji ID by typing \:bloodpoints: in Discord
BLOODPOINTS = "<:bloodpoints:000000000000000000>"  # Replace with your emoji ID
AURIC_CELLS = "<:auriccells:000000000000000000>"   # Replace with your emoji ID

# ===================================
# ROLE EMOJIS
# ===================================
KILLER = "<:killer:000000000000000000>"            # Replace with your emoji ID
SURVIVOR = "<:survivor:000000000000000000>"        # Replace with your emoji ID

# ===================================
# ITEM EMOJIS (Shop Items)
# ===================================
MEDKIT = "<:medkit:000000000000000000>"            # Replace with your emoji ID
FLASHLIGHT = "<:flashlight:000000000000000000>"    # Replace with your emoji ID
TOOLBOX = "<:toolbox:000000000000000000>"          # Replace with your emoji ID
MAP = "<:map:000000000000000000>"                  # Replace with your emoji ID
KEY = "<:key:000000000000000000>"                  # Replace with your emoji ID
FIRST_AID_KIT = "<:firstaidkit:000000000000000000>" # Replace with your emoji ID

# ===================================
# MINIGAME EMOJIS
# ===================================
HUNTING = "<:hunting:000000000000000000>"          # Replace with your emoji ID
FISHING = "<:fishing:000000000000000000>"          # Replace with your emoji ID
SCAVENGING = "<:scavenging:000000000000000000>"    # Replace with your emoji ID

# ===================================
# TRIAL & MISC EMOJIS
# ===================================
TRIAL = "<:trial:000000000000000000>"              # Replace with your emoji ID
INVENTORY = "<:inventory:000000000000000000>"      # Replace with your emoji ID
PROFILE = "<:profile:000000000000000000>"          # Replace with your emoji ID

# ===================================
# HELPER FUNCTIONS
# ===================================

def get_item_emoji(item_name):
    """
    Get custom emoji for an item name.
    Returns custom emoji if available, otherwise returns a default emoji.
    """
    emoji_map = {
        # Shop items
        'medkit': MEDKIT,
        'flashlight': FLASHLIGHT,
        'toolbox': TOOLBOX,
        'map': MAP,
        'key': KEY,
        'first aid kit': FIRST_AID_KIT,
        'engineer\'s toolbox': TOOLBOX,
        'sport flashlight': FLASHLIGHT,
        
        # Gathered items (use standard emojis as fallback)
        'fresh meat': '🥩',
        'animal hide': '🦌',
        'bone fragment': '🦴',
        'fresh fish': '🐟',
        'old boot': '👢',
        'strange relic': '🗿',
        'scrap metal': '🔩',
        'old coins': '🪙',
        'medical supplies': '💊',
        'mysterious map': '🗺️',
    }
    
    # Return custom emoji if found, otherwise default box emoji
    return emoji_map.get(item_name.lower(), '📦')

def get_role_emoji(role):
    """Get emoji for character role (Killer or Survivor)"""
    return KILLER if role == 'Killer' else SURVIVOR

def get_currency_emojis():
    """Get both currency emojis as a tuple"""
    return (BLOODPOINTS, AURIC_CELLS)

# ===================================
# USAGE EXAMPLES
# ===================================
"""
In main.py:

from emojis import *

# Use in embeds:
embed.add_field(
    name="Currency",
    value=f"{BLOODPOINTS} 10,000 BP\n{AURIC_CELLS} 50 AC"
)

# Use with items:
item_emoji = get_item_emoji("Medkit")
embed.add_field(name="Item", value=f"{item_emoji} Medkit")

# Use with roles:
role_emoji = get_role_emoji("Killer")
embed.add_field(name="Role", value=f"{role_emoji} Killer")
"""
