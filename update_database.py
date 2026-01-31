import sqlite3

# Connect to your database
conn = sqlite3.connect('game_database.db')
cursor = conn.cursor()

try:
    # Add category columns
    cursor.execute("ALTER TABLE shop_items ADD COLUMN category TEXT DEFAULT 'Miscellaneous'")
    print("✓ Added category to shop_items")
except:
    print("✗ shop_items already has category column")

try:
    cursor.execute("ALTER TABLE hunting_items ADD COLUMN category TEXT")
    print("✓ Added category to hunting_items")
except:
    print("✗ hunting_items already has category column")

try:
    cursor.execute("ALTER TABLE fishing_items ADD COLUMN category TEXT")
    print("✓ Added category to fishing_items")
except:
    print("✗ fishing_items already has category column")

try:
    cursor.execute("ALTER TABLE scavenging_items ADD COLUMN category TEXT")
    print("✓ Added category to scavenging_items")
except:
    print("✗ scavenging_items already has category column")

# Update existing shop items with categories
cursor.execute("UPDATE shop_items SET category = 'Consumables' WHERE item_name IN ('Medkit', 'First Aid Kit')")
cursor.execute("UPDATE shop_items SET category = 'Tools' WHERE item_name IN ('Toolbox', 'Flashlight', 'Engineer''s Toolbox', 'Sport Flashlight')")
cursor.execute("UPDATE shop_items SET category = 'Collectibles' WHERE item_name IN ('Map', 'Key')")
print("✓ Updated shop item categories")

# Update existing hunting items
cursor.execute("UPDATE hunting_items SET category = 'Consumables' WHERE item_name = 'Fresh Meat'")
cursor.execute("UPDATE hunting_items SET category = 'Collectibles' WHERE item_name IN ('Animal Hide', 'Bone Fragment')")
print("✓ Updated hunting item categories")

# Update existing fishing items
cursor.execute("UPDATE fishing_items SET category = 'Consumables' WHERE item_name = 'Fresh Fish'")
cursor.execute("UPDATE fishing_items SET category = 'Collectibles' WHERE item_name IN ('Strange Relic', 'Old Boot')")
print("✓ Updated fishing item categories")

# Update existing scavenging items
cursor.execute("UPDATE scavenging_items SET category = 'Collectibles' WHERE item_name IN ('Scrap Metal', 'Old Coins', 'Mysterious Map')")
cursor.execute("UPDATE scavenging_items SET category = 'Consumables' WHERE item_name = 'Medical Supplies'")
print("✓ Updated scavenging item categories")

conn.commit()
conn.close()

print("\n✅ Database updated successfully!")
