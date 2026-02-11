import sqlite3
import random

# ADMIN USER IDS - These users can edit ANY character
# Replace with YOUR Discord user ID
ADMIN_IDS = [
    790588177240555561,  # Replace this with your actual Discord ID
    210551397278679050, #Joker
    724281461053849641, #Zem
    200759921912840193, #Rhythm
    # Add more admin IDs here if needed
]

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
        
        # Add user_id column if it doesn't exist (migration for ownership)
        cursor.execute("PRAGMA table_info(profiles)")
        columns = [column[1] for column in cursor.fetchall()]
        if 'user_id' not in columns:
            cursor.execute("ALTER TABLE profiles ADD COLUMN user_id TEXT")
            print("✓ Added user_id column to profiles table for character ownership")
        
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
        
        # Add category and currency_type columns if they don't exist (migration)
        cursor.execute("PRAGMA table_info(shop_items)")
        shop_columns = [column[1] for column in cursor.fetchall()]
        if 'category' not in shop_columns:
            cursor.execute("ALTER TABLE shop_items ADD COLUMN category TEXT DEFAULT 'Miscellaneous'")
            print("✓ Added category column to shop_items table")
        if 'currency_type' not in shop_columns:
            cursor.execute("ALTER TABLE shop_items ADD COLUMN currency_type TEXT DEFAULT 'bloodpoints'")
            print("✓ Added currency_type column to shop_items table")
        
        # Trial messages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trial_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL,
                performance_level INTEGER NOT NULL,
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
                item_name TEXT,
                message TEXT NOT NULL
            )
        ''')
        
        # Fishing items table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fishing_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_name TEXT,
                message TEXT NOT NULL
            )
        ''')
        
        # Scavenging items table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scavenging_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_name TEXT,
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
                # Killer messages - Performance 0 (0 Kills - Total Failure)
                ("Killer", 0, "A complete failure. All survivors escaped. The Entity is furious with your incompetence."),
                ("Killer", 0, "Humiliating defeat. Not a single survivor fell to your blade. Shame fills the fog."),
                ("Killer", 0, "The survivors toyed with you. All four escaped unscathed. You have disappointed The Entity."),
                
                # Killer messages - Performance 1 (1 Kill - Poor)
                ("Killer", 1, "The survivors proved elusive. You managed one sacrifice, but three escaped into the fog."),
                ("Killer", 1, "Your hunt was challenging. Only one survivor fell to your blade tonight."),
                ("Killer", 1, "The Entity whispers its disappointment. Most survivors escaped your grasp."),
                
                # Killer messages - Performance 2 (2 Kills - Average)
                ("Killer", 2, "A decent hunt. Two survivors sacrificed, but two escaped through the gates."),
                ("Killer", 2, "You stalked through the fog with moderate success. Half the survivors fell."),
                ("Killer", 2, "The trial ended in balance. Two hooks, two escapes."),
                
                # Killer messages - Performance 3 (3 Kills - Good)
                ("Killer", 3, "An impressive display of power! Three survivors sacrificed, only one escaped."),
                ("Killer", 3, "Your brutal efficiency earned a strong victory. Three fell to The Entity."),
                ("Killer", 3, "You dominated the trial. Three survivors on hooks, one narrowly escaped."),
                
                # Killer messages - Performance 4 (4 Kills - Perfect)
                ("Killer", 4, "FLAWLESS VICTORY! All survivors sacrificed. The Entity is greatly pleased."),
                ("Killer", 4, "The trial ended with all survivors on hooks. A perfect sacrifice to The Entity."),
                ("Killer", 4, "Total domination! No one survived. The fog consumes all."),
                
                # Survivor messages - Performance 0 (0 Escapes - Total Failure)
                ("Survivor", 0, "Total annihilation. All four survivors were sacrificed. The killer was unstoppable."),
                ("Survivor", 0, "A massacre. No one escaped. The Entity claims all four souls tonight."),
                ("Survivor", 0, "Complete defeat. The killer showed no mercy. All survivors fell to the hooks."),
                
                # Survivor messages - Performance 1 (1 Escape - Poor)
                ("Survivor", 1, "You barely made it out alive. Three teammates fell, but you escaped alone."),
                ("Survivor", 1, "A desperate escape. The killer claimed your teammates, but you found the hatch."),
                ("Survivor", 1, "Survival came at a cost. Only you made it through the gates."),
                
                # Survivor messages - Performance 2 (2 Escapes - Average)
                ("Survivor", 2, "A difficult trial. You and one teammate escaped, but two were sacrificed."),
                ("Survivor", 2, "Half the team made it out. A bittersweet escape through the fog."),
                ("Survivor", 2, "Two escaped, two sacrificed. The killer fought well tonight."),
                
                # Survivor messages - Performance 3 (3 Escapes - Good)
                ("Survivor", 3, "Excellent teamwork! Three survivors escaped, though one fell to the killer."),
                ("Survivor", 3, "You unhooked your teammates and healed the wounded. Three made it out!"),
                ("Survivor", 3, "An impressive trial. Three survivors through the gates, one sacrificed."),
                
                # Survivor messages - Performance 4 (4 Escapes - Perfect)
                ("Survivor", 4, "PERFECT ESCAPE! All four survivors made it out. The killer stands defeated!"),
                ("Survivor", 4, "Working together, you managed to repair all generators and escape with your team."),
                ("Survivor", 4, "You looped the killer for five generators. All four survivors escaped to safety!")
            ]
            cursor.executemany("INSERT INTO trial_messages (role, performance_level, message) VALUES (?, ?, ?)", trial_messages)
        
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
                (None, "Your hunt was unsuccessful. The prey escaped into the fog."),
                (None, "You searched the woods but found nothing. Better luck next time.")
            ]
            cursor.executemany("INSERT INTO hunting_items (item_name, message) VALUES (?, ?)", hunting_items)
        
        # Check and add fishing items
        cursor.execute("SELECT COUNT(*) FROM fishing_items")
        if cursor.fetchone()[0] == 0:
            fishing_items = [
                ("Fresh Fish", "You caught a fresh fish from the murky waters!"),
                ("Old Boot", "You reeled in... an old boot. At least it's something."),
                ("Strange Relic", "Something ancient surfaced. A strange relic from the depths."),
                (None, "The fish weren't biting today. You caught nothing."),
                (None, "Your line got tangled. No catch this time.")
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
                (None, "Your search turned up empty. Nothing of value here."),
                (None, "You combed through the area but found nothing useful.")
            ]
            cursor.executemany("INSERT INTO scavenging_items (item_name, message) VALUES (?, ?)", scavenging_items)
        
        conn.commit()
        conn.close()
    
    # Profile Methods
    def create_profile(self, name, role, user_id):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO profiles (name, role, user_id) VALUES (?, ?, ?)", 
                         (name, role, str(user_id)))
            conn.commit()
            conn.close()
            return True, f"Profile created for {name}"
        except sqlite3.IntegrityError:
            return False, f"Profile {name} already exists!"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def check_ownership(self, name, user_id):
        """Check if user owns the character. Returns (is_owner, message)"""
        try:
            # ADMIN BYPASS - Admins can edit everything
            if int(user_id) in ADMIN_IDS:
                return True, "Admin access"
            
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM profiles WHERE name = ?", (name,))
            result = cursor.fetchone()
            conn.close()
            
            if not result:
                return False, f"Character **{name}** not found!"
            
            owner_id = result[0]
            
            # If user_id is NULL (legacy character created before ownership), anyone can edit
            if owner_id is None:
                return True, "Legacy character (no owner)"
            
            # Check if user is the owner
            if str(owner_id) == str(user_id):
                return True, "You own this character"
            
            return False, f"❌ You don't own **{name}**! Only the creator can edit this character."
            
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def claim_character(self, name, user_id):
        """Claim an unowned (legacy) character"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT user_id FROM profiles WHERE name = ?", (name,))
            result = cursor.fetchone()
            
            if not result:
                conn.close()
                return False, f"Character **{name}** not found!"
            
            owner_id = result[0]
            
            if owner_id is not None:
                conn.close()
                return False, f"**{name}** is already owned by someone!"
            
            # Claim it
            cursor.execute("UPDATE profiles SET user_id = ? WHERE name = ?", (str(user_id), name))
            conn.commit()
            conn.close()
            return True, f"✅ You now own **{name}**!"
            
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def assign_owner(self, character_name, new_owner_id):
        """Manually assign ownership of a character (admin only)"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT name FROM profiles WHERE name = ?", (character_name,))
            if not cursor.fetchone():
                conn.close()
                return False, f"Character **{character_name}** not found!"
            
            cursor.execute("UPDATE profiles SET user_id = ? WHERE name = ?", 
                          (str(new_owner_id), character_name))
            conn.commit()
            conn.close()
            return True, f"✅ Assigned **{character_name}** to user ID {new_owner_id}"
            
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
        
        # Get inventory with categories from shop_items
        cursor.execute("""
            SELECT i.item_name, COUNT(*) as quantity, COALESCE(s.category, 'Miscellaneous') as category
            FROM inventory i
            LEFT JOIN shop_items s ON i.item_name = s.item_name
            WHERE i.character_name = ?
            GROUP BY i.item_name, s.category
            ORDER BY s.category, i.item_name
        """, (name,))
        results = cursor.fetchall()
        conn.close()
        
        # Categorize items
        categorized = {
            'Consumables': [],
            'Tools': [],
            'Collectibles': [],
            'Miscellaneous': [],
            'NSFW': [],
        }
        
        for item_name, quantity, category in results:
            item_data = {'item_name': item_name, 'quantity': quantity}
            
            # Use the category from shop_items
            if category in categorized:
                categorized[category].append(item_data)
            else:
                # If category doesn't exist in our dict, add to Miscellaneous
                categorized['Miscellaneous'].append(item_data)
        
        return categorized
    
    # Shop Methods
    def buy_item(self, name, item_name):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Check if profile exists and get both currencies
            cursor.execute("SELECT bloodpoints, auric_cells FROM profiles WHERE name = ?", (name,))
            result = cursor.fetchone()
            if not result:
                conn.close()
                return False, f"Profile {name} not found!", 0, None
            
            bloodpoints, auric_cells = result[0], result[1]
            
            # Check if item exists in shop and get its currency type
            cursor.execute("SELECT price, currency_type FROM shop_items WHERE item_name = ?", (item_name,))
            result = cursor.fetchone()
            if not result:
                conn.close()
                return False, f"Item {item_name} not found in shop!", 0, None
            
            price = result[0]
            currency_type = result[1] if result[1] else 'bloodpoints'  # Default to bloodpoints if NULL
            
            # Check currency and balance based on type
            if currency_type == 'auric_cells':
                current_balance = auric_cells
                currency_name = "Auric Cells"
                currency_column = "auric_cells"
            else:
                current_balance = bloodpoints
                currency_name = "Bloodpoints"
                currency_column = "bloodpoints"
            
            # Check if enough currency
            if current_balance < price:
                conn.close()
                return False, f"Insufficient {currency_name}! This item costs **{price:,}**, you have **{current_balance:,}**.", price, currency_type
            
            # Deduct currency and add item
            cursor.execute(f"UPDATE profiles SET {currency_column} = {currency_column} - ? WHERE name = ?", (price, name))
            cursor.execute("INSERT INTO inventory (character_name, item_name) VALUES (?, ?)", (name, item_name))
            
            conn.commit()
            conn.close()
            return True, f"Purchased {item_name}", price, currency_type
        except Exception as e:
            return False, f"Error: {str(e)}", 0, None
    
    def buy_items_bulk(self, name, item_names):
        """Buy multiple items at once. Returns (success, message, total_price, currency_type, items_purchased)"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Check if profile exists and get both currencies
            cursor.execute("SELECT bloodpoints, auric_cells FROM profiles WHERE name = ?", (name,))
            result = cursor.fetchone()
            if not result:
                conn.close()
                return False, f"Profile {name} not found!", 0, None, []
            
            bloodpoints, auric_cells = result[0], result[1]
            
            # Get all items and calculate total per currency type
            items_to_buy = []
            bp_total = 0
            ac_total = 0
            
            for item_name in item_names:
                cursor.execute("SELECT price, currency_type FROM shop_items WHERE item_name = ?", (item_name,))
                result = cursor.fetchone()
                
                if not result:
                    conn.close()
                    return False, f"Item **{item_name}** not found in shop!", 0, None, []
                
                price = result[0]
                currency_type = result[1] if result[1] else 'bloodpoints'
                
                items_to_buy.append({
                    'name': item_name,
                    'price': price,
                    'currency_type': currency_type
                })
                
                if currency_type == 'auric_cells':
                    ac_total += price
                else:
                    bp_total += price
            
            # Check if mixing currencies
            if bp_total > 0 and ac_total > 0:
                conn.close()
                return False, "❌ Cannot mix Bloodpoints and Auric Cells items in one purchase! Please buy them separately.", 0, None, []
            
            # Determine which currency we're using
            if ac_total > 0:
                total_price = ac_total
                currency_type = 'auric_cells'
                current_balance = auric_cells
                currency_name = "Auric Cells"
                currency_column = "auric_cells"
            else:
                total_price = bp_total
                currency_type = 'bloodpoints'
                current_balance = bloodpoints
                currency_name = "Bloodpoints"
                currency_column = "bloodpoints"
            
            # Check if enough currency
            if current_balance < total_price:
                conn.close()
                return False, f"Insufficient {currency_name}! Total cost is **{total_price:,}**, you have **{current_balance:,}**.", total_price, currency_type, []
            
            # Deduct currency and add all items
            cursor.execute(f"UPDATE profiles SET {currency_column} = {currency_column} - ? WHERE name = ?", (total_price, name))
            
            for item in items_to_buy:
                cursor.execute("INSERT INTO inventory (character_name, item_name) VALUES (?, ?)", (name, item['name']))
            
            conn.commit()
            conn.close()
            
            item_names_list = [item['name'] for item in items_to_buy]
            return True, f"Purchased {len(items_to_buy)} items", total_price, currency_type, item_names_list
            
        except Exception as e:
            return False, f"Error: {str(e)}", 0, None, []
    
    def use_items(self, name, item_names):
        """Use (remove) multiple items from inventory. Returns (success, message, items_used)"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Check if profile exists
            cursor.execute("SELECT name FROM profiles WHERE name = ?", (name,))
            if not cursor.fetchone():
                conn.close()
                return False, f"Profile **{name}** not found!", []
            
            items_used = []
            items_not_found = []
            
            for item_name in item_names:
                # Check if item exists in inventory
                cursor.execute("SELECT id FROM inventory WHERE character_name = ? AND item_name = ? LIMIT 1", 
                             (name, item_name))
                result = cursor.fetchone()
                
                if result:
                    # Remove one instance of the item
                    cursor.execute("DELETE FROM inventory WHERE id = ?", (result[0],))
                    items_used.append(item_name)
                else:
                    items_not_found.append(item_name)
            
            conn.commit()
            conn.close()
            
            if not items_used:
                return False, f"None of the items were found in **{name}**'s inventory!", []
            
            if items_not_found:
                message = f"Some items not found: **{', '.join(items_not_found)}**"
                return True, message, items_used
            
            return True, "Items used successfully", items_used
            
        except Exception as e:
            return False, f"Error: {str(e)}", []
    
    # Trial Methods
    def complete_trial(self, name):
        # Get the character's profile to check their role
        profile = self.get_profile(name)
        if not profile:
            return None
        
        # Extract the role (either "Killer" or "Survivor")
        role = profile['role']
        
        # Performance-based rewards
        # Random performance: 0-4 escapes/kills
        performance = random.randint(0, 4)
        
        # Get a RANDOM trial message for THIS SPECIFIC ROLE AND PERFORMANCE LEVEL
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT message FROM trial_messages WHERE role = ? AND performance_level = ? ORDER BY RANDOM() LIMIT 1", 
            (role, performance)
        )
        result = cursor.fetchone()
        
        # Use the random message, or fallback if none found
        message = result[0] if result else f"You completed a trial as {role}."
        
        # Bloodpoints: 5,000 per escape/kill (0 for total failure)
        # 0 = 0 BP
        # 1 = 5,000 BP
        # 2 = 10,000 BP
        # 3 = 15,000 BP
        # 4 = 20,000 BP
        bloodpoints = performance * 5000
        
        # Auric Cells: 1 per escape/kill (0 for total failure)
        # 0 = 0 AC
        # 1 = 1 AC
        # 2 = 2 AC
        # 3 = 3 AC
        # 4 = 4 AC
        auric_cells = performance
        
        # Performance description
        if role == "Killer":
            performance_text = {
                0: "0 Kills (Total Failure)",
                1: "1 Kill",
                2: "2 Kills",
                3: "3 Kills",
                4: "4 Kills (Perfect!)"
            }
        else:  # Survivor
            performance_text = {
                0: "0 Survivors Escaped (Total Failure)",
                1: "1 Survivor Escaped",
                2: "2 Survivors Escaped",
                3: "3 Survivors Escaped",
                4: "4 Survivors Escaped (Perfect!)"
            }
        
        # Add the rewards to the character's profile (only if performance > 0)
        if performance > 0:
            cursor.execute(
                "UPDATE profiles SET bloodpoints = bloodpoints + ?, auric_cells = auric_cells + ? WHERE name = ?",
                (bloodpoints, auric_cells, name)
            )
            conn.commit()
        
        conn.close()
        
        # Return all the information to display in Discord
        return {
            'role': role,                      # "Killer" or "Survivor"
            'message': message,                # Random message from database matching performance
            'bloodpoints': bloodpoints,        # 0 / 5,000 / 10,000 / 15,000 / 20,000
            'auric_cells': auric_cells,       # 0 / 1 / 2 / 3 / 4
            'performance': performance,        # 0 / 1 / 2 / 3 / 4
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
        cursor.execute("SELECT item_name, message, description FROM hunting_items ORDER BY RANDOM() LIMIT 1")
        result = cursor.fetchone()
        
        item_name = result[0]
        message = result[1]
        description = result[2] if len(result) > 2 else message  # Fallback to message if no description
        
        # Only add to inventory if item_name is valid (not None, empty, or 'none'/'nothing')
        if item_name and item_name.strip() and item_name.lower() not in ['none', 'nothing', 'null']:
            cursor.execute("INSERT INTO inventory (character_name, item_name) VALUES (?, ?)", (name, item_name))
            conn.commit()
        
        conn.close()
        
        return {
            'item': item_name if (item_name and item_name.strip() and item_name.lower() not in ['none', 'nothing', 'null']) else None,
            'message': message,
            'description': description
        }
    
    def fishing_minigame(self, name):
        profile = self.get_profile(name)
        if not profile:
            return None
        
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT item_name, message, description FROM fishing_items ORDER BY RANDOM() LIMIT 1")
        result = cursor.fetchone()
        
        item_name = result[0]
        message = result[1]
        description = result[2] if len(result) > 2 else message  # Fallback to message if no description
        
        # Only add to inventory if item_name is valid (not None, empty, or 'none'/'nothing')
        if item_name and item_name.strip() and item_name.lower() not in ['none', 'nothing', 'null']:
            cursor.execute("INSERT INTO inventory (character_name, item_name) VALUES (?, ?)", (name, item_name))
            conn.commit()
        
        conn.close()
        
        return {
            'item': item_name if (item_name and item_name.strip() and item_name.lower() not in ['none', 'nothing', 'null']) else None,
            'message': message,
            'description': description
        }
    
    def scavenging_minigame(self, name):
        profile = self.get_profile(name)
        if not profile:
            return None
        
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT item_name, message, description FROM scavenging_items ORDER BY RANDOM() LIMIT 1")
        result = cursor.fetchone()
        
        item_name = result[0]
        message = result[1]
        description = result[2] if len(result) > 2 else message  # Fallback to message if no description
        
        # Only add to inventory if item_name is valid (not None, empty, or 'none'/'nothing')
        if item_name and item_name.strip() and item_name.lower() not in ['none', 'nothing', 'null']:
            cursor.execute("INSERT INTO inventory (character_name, item_name) VALUES (?, ?)", (name, item_name))
            conn.commit()
        
        conn.close()
        
        return {
            'item': item_name if (item_name and item_name.strip() and item_name.lower() not in ['none', 'nothing', 'null']) else None,
            'message': message,
            'description': description
        }
