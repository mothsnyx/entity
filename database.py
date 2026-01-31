import sqlite3
import random

class Database:
    def __init__(self, db_name="game_database.db"):
        self.db_name = db_name
        self.init_database()
        self.populate_initial_data()
    
    def get_connection(self):
        return sqlite3.connect(self.db_name)
    
    def init_database(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Profiles table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                role TEXT NOT NULL,
                bloodpoints INTEGER DEFAULT 0,
                auric_cells INTEGER DEFAULT 0
            )
        ''')
        
        # Inventory table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                character_name TEXT NOT NULL,
                item_name TEXT NOT NULL,
                FOREIGN KEY (character_name) REFERENCES profiles(name) ON DELETE CASCADE
            )
        ''')
        
        # Shop items table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS shop_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_name TEXT UNIQUE NOT NULL,
                price INTEGER NOT NULL,
                description TEXT
            )
        ''')
        
        # Trial messages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trial_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL,
                message TEXT NOT NULL
            )
        ''')
        
        # Realms table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS realms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
        ''')
        
        # Hunting items table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hunting_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_name TEXT NOT NULL,
                message TEXT NOT NULL
            )
        ''')
        
        # Fishing items table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fishing_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_name TEXT NOT NULL,
                message TEXT NOT NULL
            )
        ''')
        
        # Scavenging items table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scavenging_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_name TEXT NOT NULL,
                message TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def populate_initial_data(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Check if data already exists
        cursor.execute("SELECT COUNT(*) FROM shop_items")
        if cursor.fetchone()[0] == 0:
            # Add shop items
            shop_items = [
                ("Medkit", 3000, "Heal yourself or others"),
                ("Toolbox", 4000, "Repair generators faster"),
                ("Flashlight", 2500, "Blind the killer"),
                ("Map", 3500, "Track objectives"),
                ("Key", 5000, "Open the hatch"),
                ("First Aid Kit", 2000, "Basic healing item"),
                ("Engineer's Toolbox", 6000, "Advanced repair tool"),
                ("Sport Flashlight", 4500, "High-quality flashlight")
            ]
            cursor.executemany("INSERT INTO shop_items (item_name, price, description) VALUES (?, ?, ?)", shop_items)
        
        # Check and add trial messages
        cursor.execute("SELECT COUNT(*) FROM trial_messages")
        if cursor.fetchone()[0] == 0:
            trial_messages = [
                # Killer messages
                ("Killer", "You stalked through the fog, your presence striking fear into the survivors. The Entity is pleased."),
                ("Killer", "The hunt was exhilarating. You hooked multiple survivors and asserted your dominance."),
                ("Killer", "Your brutal efficiency earned you a ruthless victory. The survivors never stood a chance."),
                ("Killer", "You patrolled the generators with precision, cutting off all escape routes."),
                ("Killer", "The trial ended with all survivors on hooks. A perfect sacrifice to The Entity."),
                # Survivor messages
                ("Survivor", "You narrowly escaped through the exit gates, leaving your teammates behind in the fog."),
                ("Survivor", "Working together, you managed to repair all generators and escape with your team."),
                ("Survivor", "You were hooked but managed to escape. Your determination earned you survival."),
                ("Survivor", "You unhooked your teammates and healed the wounded. Your altruism was rewarded."),
                ("Survivor", "The hatch appeared just in time. You slipped through as the killer closed in."),
                ("Survivor", "You looped the killer for five generators. Your skills bought your team precious time.")
            ]
            cursor.executemany("INSERT INTO trial_messages (role, message) VALUES (?, ?)", trial_messages)
        
        # Check and add realms
        cursor.execute("SELECT COUNT(*) FROM realms")
        if cursor.fetchone()[0] == 0:
            realms = [
                ("MacMillan Estate",),
                ("Autohaven Wreckers",),
                ("Coldwind Farm",),
                ("Crotus Prenn Asylum",),
                ("Haddonfield",),
                ("Backwater Swamp",),
                ("Léry's Memorial Institute",),
                ("Red Forest",),
                ("Springwood",),
                ("Gideon Meat Plant",),
                ("Yamaoka Estate",),
                ("Ormond",),
                ("Hawkins National Laboratory",),
                ("Grave of Glenvale",),
                ("Silent Hill",),
                ("Raccoon City",),
                ("Forsaken Boneyard",)
            ]
            cursor.executemany("INSERT INTO realms (name) VALUES (?)", realms)
        
        # Check and add hunting items
        cursor.execute("SELECT COUNT(*) FROM hunting_items")
        if cursor.fetchone()[0] == 0:
            hunting_items = [
                ("Fresh Meat", "You tracked and hunted a wild animal. Fresh meat acquired!"),
                ("Animal Hide", "You successfully hunted down prey and collected its hide."),
                ("Bone Fragment", "Your hunt was successful. You collected bone fragments."),
                ("Nothing", "Your hunt was unsuccessful. The prey escaped into the fog."),
                ("Nothing", "You searched the woods but found nothing. Better luck next time.")
            ]
            cursor.executemany("INSERT INTO hunting_items (item_name, message) VALUES (?, ?)", hunting_items)
        
        # Check and add fishing items
        cursor.execute("SELECT COUNT(*) FROM fishing_items")
        if cursor.fetchone()[0] == 0:
            fishing_items = [
                ("Fresh Fish", "You caught a fresh fish from the murky waters!"),
                ("Old Boot", "You reeled in... an old boot. At least it's something."),
                ("Strange Relic", "Something ancient surfaced. A strange relic from the depths."),
                ("Nothing", "The fish weren't biting today. You caught nothing."),
                ("Nothing", "Your line got tangled. No catch this time.")
            ]
            cursor.executemany("INSERT INTO fishing_items (item_name, message) VALUES (?, ?)", fishing_items)
        
        # Check and add scavenging items
        cursor.execute("SELECT COUNT(*) FROM scavenging_items")
        if cursor.fetchone()[0] == 0:
            scavenging_items = [
                ("Scrap Metal", "You found some useful scrap metal among the debris."),
                ("Old Coins", "You discovered a stash of old coins hidden away."),
                ("Medical Supplies", "You scavenged some medical supplies from an abandoned building."),
                ("Mysterious Map", "You found a mysterious map with strange markings."),
                ("Nothing", "Your search turned up empty. Nothing of value here."),
                ("Nothing", "You combed through the area but found nothing useful.")
            ]
            cursor.executemany("INSERT INTO scavenging_items (item_name, message) VALUES (?, ?)", scavenging_items)
        
        conn.commit()
        conn.close()
    
    # Profile Methods
    def create_profile(self, name, role):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO profiles (name, role) VALUES (?, ?)", (name, role))
            conn.commit()
            conn.close()
            return True, f"Profile created for {name}"
        except sqlite3.IntegrityError:
            return False, f"Profile {name} already exists!"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def edit_profile_name(self, old_name, new_name):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM profiles WHERE name = ?", (old_name,))
            if not cursor.fetchone():
                conn.close()
                return False, f"Profile {old_name} not found!"
            
            cursor.execute("UPDATE profiles SET name = ? WHERE name = ?", (new_name, old_name))
            cursor.execute("UPDATE inventory SET character_name = ? WHERE character_name = ?", (new_name, old_name))
            conn.commit()
            conn.close()
            return True, f"Profile renamed to {new_name}"
        except sqlite3.IntegrityError:
            return False, f"Profile {new_name} already exists!"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def edit_profile_role(self, name, new_role):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM profiles WHERE name = ?", (name,))
            if not cursor.fetchone():
                conn.close()
                return False, f"Profile {name} not found!"
            
            cursor.execute("UPDATE profiles SET role = ? WHERE name = ?", (new_role, name))
            conn.commit()
            conn.close()
            return True, f"Role updated to {new_role}"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def delete_profile(self, name):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM profiles WHERE name = ?", (name,))
            if not cursor.fetchone():
                conn.close()
                return False, f"Profile {name} not found!"
            
            cursor.execute("DELETE FROM profiles WHERE name = ?", (name,))
            cursor.execute("DELETE FROM inventory WHERE character_name = ?", (name,))
            conn.commit()
            conn.close()
            return True, f"Profile {name} deleted"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def get_profile(self, name):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM profiles WHERE name = ?", (name,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'id': result[0],
                'name': result[1],
                'role': result[2],
                'bloodpoints': result[3],
                'auric_cells': result[4]
            }
        return None
    
    # Currency Methods
    def add_currency(self, name, currency_type, amount):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM profiles WHERE name = ?", (name,))
            if not cursor.fetchone():
                conn.close()
                return False, f"Profile {name} not found!"
            
            cursor.execute(f"UPDATE profiles SET {currency_type} = {currency_type} + ? WHERE name = ?", (amount, name))
            conn.commit()
            conn.close()
            return True, f"Added {amount} {currency_type}"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def remove_currency(self, name, currency_type, amount):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute(f"SELECT {currency_type} FROM profiles WHERE name = ?", (name,))
            result = cursor.fetchone()
            
            if not result:
                conn.close()
                return False, f"Profile {name} not found!"
            
            current_amount = result[0]
            if current_amount < amount:
                conn.close()
                return False, f"Insufficient {currency_type}! Current: {current_amount}"
            
            cursor.execute(f"UPDATE profiles SET {currency_type} = {currency_type} - ? WHERE name = ?", (amount, name))
            conn.commit()
            conn.close()
            return True, f"Removed {amount} {currency_type}"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    # Inventory Methods
    def add_item(self, name, item_name):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM profiles WHERE name = ?", (name,))
            if not cursor.fetchone():
                conn.close()
                return False, f"Profile {name} not found!"
            
            cursor.execute("INSERT INTO inventory (character_name, item_name) VALUES (?, ?)", (name, item_name))
            conn.commit()
            conn.close()
            return True, f"Added {item_name} to inventory"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def remove_item(self, name, item_name):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM inventory WHERE character_name = ? AND item_name = ?", (name, item_name))
            if not cursor.fetchone():
                conn.close()
                return False, f"{item_name} not found in {name}'s inventory!"
            
            cursor.execute("DELETE FROM inventory WHERE character_name = ? AND item_name = ? LIMIT 1", (name, item_name))
            conn.commit()
            conn.close()
            return True, f"Removed {item_name} from inventory"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def get_inventory(self, name):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Count each item and group by name
        cursor.execute("""
            SELECT item_name, COUNT(*) as quantity 
            FROM inventory 
            WHERE character_name = ? 
            GROUP BY item_name
            ORDER BY item_name
        """, (name,))
        results = cursor.fetchall()
        conn.close()
        
        # Categorize items
        categorized = {
            'Consumables': [],
            'Tools': [],
            'Collectibles': [],
            'Miscellaneous': []
        }
        
        # Item categories mapping
        consumables = ['medkit', 'first aid kit', 'fresh meat', 'fresh fish', 'medical supplies']
        tools = ['toolbox', 'flashlight', 'engineer\'s toolbox', 'sport flashlight']
        collectibles = ['map', 'key', 'animal hide', 'bone fragment', 'strange relic', 'old coins', 'mysterious map']
        
        for item_name, quantity in results:
            item_lower = item_name.lower()
            item_data = {'item_name': item_name, 'quantity': quantity}
            
            if item_lower in consumables:
                categorized['Consumables'].append(item_data)
            elif item_lower in tools:
                categorized['Tools'].append(item_data)
            elif item_lower in collectibles:
                categorized['Collectibles'].append(item_data)
            else:
                categorized['Miscellaneous'].append(item_data)
        
        return categorized
    
    # Shop Methods
    def buy_item(self, name, item_name):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Check if profile exists
            cursor.execute("SELECT bloodpoints FROM profiles WHERE name = ?", (name,))
            result = cursor.fetchone()
            if not result:
                conn.close()
                return False, f"Profile {name} not found!", 0
            
            bloodpoints = result[0]
            
            # Check if item exists in shop
            cursor.execute("SELECT price FROM shop_items WHERE item_name = ?", (item_name,))
            result = cursor.fetchone()
            if not result:
                conn.close()
                return False, f"Item {item_name} not found in shop!", 0
            
            price = result[0]
            
            # Check if enough currency
            if bloodpoints < price:
                conn.close()
                return False, f"Insufficient Bloodpoints! Need {price:,}, have {bloodpoints:,}", price
            
            # Deduct currency and add item
            cursor.execute("UPDATE profiles SET bloodpoints = bloodpoints - ? WHERE name = ?", (price, name))
            cursor.execute("INSERT INTO inventory (character_name, item_name) VALUES (?, ?)", (name, item_name))
            
            conn.commit()
            conn.close()
            return True, f"Purchased {item_name}", price
        except Exception as e:
            return False, f"Error: {str(e)}", 0
    
    # Trial Methods
    def complete_trial(self, name):
        # Get the character's profile to check their role
        profile = self.get_profile(name)
        if not profile:
            return None
        
        # Extract the role (either "Killer" or "Survivor")
        role = profile['role']
        
        # Get a RANDOM trial message for THIS SPECIFIC ROLE
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT message FROM trial_messages WHERE role = ? ORDER BY RANDOM() LIMIT 1", 
            (role,)
        )
        result = cursor.fetchone()
        
        # Use the random message, or fallback if none found
        message = result[0] if result else f"You completed a trial as {role}."
        
        # Performance-based rewards
        # Random performance: 1-4 escapes/kills
        performance = random.randint(1, 4)
        
        # Bloodpoints: 5,000 per escape/kill
        # 1 = 5,000 BP
        # 2 = 10,000 BP
        # 3 = 15,000 BP
        # 4 = 20,000 BP
        bloodpoints = performance * 5000
        
        # Auric Cells: 1 per escape/kill
        # 1 = 1 AC
        # 2 = 2 AC
        # 3 = 3 AC
        # 4 = 4 AC
        auric_cells = performance
        
        # Performance description
        if role == "Killer":
            performance_text = {
                1: "1 Kill",
                2: "2 Kills",
                3: "3 Kills",
                4: "4 Kills (Perfect!)"
            }
        else:  # Survivor
            performance_text = {
                1: "1 Survivor Escaped",
                2: "2 Survivors Escaped",
                3: "3 Survivors Escaped",
                4: "4 Survivors Escaped (Perfect!)"
            }
        
        # Add the rewards to the character's profile
        cursor.execute(
            "UPDATE profiles SET bloodpoints = bloodpoints + ?, auric_cells = auric_cells + ? WHERE name = ?",
            (bloodpoints, auric_cells, name)
        )
        conn.commit()
        conn.close()
        
        # Return all the information to display in Discord
        return {
            'role': role,                      # "Killer" or "Survivor"
            'message': message,                # Random message from database
            'bloodpoints': bloodpoints,        # 5,000 / 10,000 / 15,000 / 20,000
            'auric_cells': auric_cells,       # 1 / 2 / 3 / 4
            'performance': performance,        # 1 / 2 / 3 / 4
            'performance_text': performance_text[performance]  # Display text
        }
    
    # Other Methods
    def get_random_realm(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM realms ORDER BY RANDOM() LIMIT 1")
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else "Unknown Realm"
    
    def hunting_minigame(self, name):
        profile = self.get_profile(name)
        if not profile:
            return None
        
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT item_name, message FROM hunting_items ORDER BY RANDOM() LIMIT 1")
        result = cursor.fetchone()
        
        item_name = result[0]
        message = result[1]
        
        if item_name:
            cursor.execute("INSERT INTO inventory (character_name, item_name) VALUES (?, ?)", (name, item_name))
            conn.commit()
        
        conn.close()
        
        return {
            'item': item_name,
            'message': message
        }
    
    def fishing_minigame(self, name):
        profile = self.get_profile(name)
        if not profile:
            return None
        
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT item_name, message FROM fishing_items ORDER BY RANDOM() LIMIT 1")
        result = cursor.fetchone()
        
        item_name = result[0]
        message = result[1]
        
        if item_name:
            cursor.execute("INSERT INTO inventory (character_name, item_name) VALUES (?, ?)", (name, item_name))
            conn.commit()
        
        conn.close()
        
        return {
            'item': item_name,
            'message': message
        }
    
    def scavenging_minigame(self, name):
        profile = self.get_profile(name)
        if not profile:
            return None
        
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT item_name, message FROM scavenging_items ORDER BY RANDOM() LIMIT 1")
        result = cursor.fetchone()
        
        item_name = result[0]
        message = result[1]
        
        if item_name:
            cursor.execute("INSERT INTO inventory (character_name, item_name) VALUES (?, ?)", (name, item_name))
            conn.commit()
        
        conn.close()
        
        return {
            'item': item_name,
            'message': message
        }
