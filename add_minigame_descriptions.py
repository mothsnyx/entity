import sqlite3

# Connect to your database
conn = sqlite3.connect('game_database.db')
cursor = conn.cursor()

print("=" * 50)
print("ADDING DESCRIPTION COLUMNS TO MINIGAME TABLES")
print("=" * 50)

# Add description columns
try:
    cursor.execute("ALTER TABLE hunting_items ADD COLUMN description TEXT")
    print("✓ Added description to hunting_items")
except sqlite3.OperationalError as e:
    if "duplicate column" in str(e).lower():
        print("✗ hunting_items already has description column")
    else:
        print(f"✗ Error with hunting_items: {e}")

try:
    cursor.execute("ALTER TABLE fishing_items ADD COLUMN description TEXT")
    print("✓ Added description to fishing_items")
except sqlite3.OperationalError as e:
    if "duplicate column" in str(e).lower():
        print("✗ fishing_items already has description column")
    else:
        print(f"✗ Error with fishing_items: {e}")

try:
    cursor.execute("ALTER TABLE scavenging_items ADD COLUMN description TEXT")
    print("✓ Added description to scavenging_items")
except sqlite3.OperationalError as e:
    if "duplicate column" in str(e).lower():
        print("✗ scavenging_items already has description column")
    else:
        print(f"✗ Error with scavenging_items: {e}")

# Commit the changes
conn.commit()

print("\n" + "=" * 50)
print("ADDING DEFAULT DESCRIPTIONS TO EXISTING ITEMS")
print("=" * 50)

# Add some example descriptions to existing items
try:
    cursor.execute("UPDATE hunting_items SET description = 'You skillfully tracked and hunted wild game.' WHERE item_name = 'Fresh Meat'")
    cursor.execute("UPDATE hunting_items SET description = 'You successfully hunted and collected valuable hide.' WHERE item_name = 'Animal Hide'")
    cursor.execute("UPDATE hunting_items SET description = 'Your hunt yielded useful bone fragments.' WHERE item_name = 'Bone Fragment'")
    cursor.execute("UPDATE hunting_items SET description = 'Despite your efforts, the prey escaped into the fog.' WHERE item_name IS NULL")
    print("✓ Added descriptions to hunting items")
except Exception as e:
    print(f"✗ Error updating hunting descriptions: {e}")

try:
    cursor.execute("UPDATE fishing_items SET description = 'You caught a fresh fish from the murky waters!' WHERE item_name = 'Fresh Fish'")
    cursor.execute("UPDATE fishing_items SET description = 'You reeled in an old boot. Better than nothing!' WHERE item_name = 'Old Boot'")
    cursor.execute("UPDATE fishing_items SET description = 'Something ancient surfaced from the depths.' WHERE item_name = 'Strange Relic'")
    cursor.execute("UPDATE fishing_items SET description = 'The fish were not biting today.' WHERE item_name IS NULL")
    print("✓ Added descriptions to fishing items")
except Exception as e:
    print(f"✗ Error updating fishing descriptions: {e}")

try:
    cursor.execute("UPDATE scavenging_items SET description = 'You found useful scrap metal among the debris.' WHERE item_name = 'Scrap Metal'")
    cursor.execute("UPDATE scavenging_items SET description = 'You discovered a stash of old coins!' WHERE item_name = 'Old Coins'")
    cursor.execute("UPDATE scavenging_items SET description = 'You scavenged medical supplies from an abandoned building.' WHERE item_name = 'Medical Supplies'")
    cursor.execute("UPDATE scavenging_items SET description = 'You found a mysterious map with strange markings.' WHERE item_name = 'Mysterious Map'")
    cursor.execute("UPDATE scavenging_items SET description = 'Your search turned up empty.' WHERE item_name IS NULL")
    print("✓ Added descriptions to scavenging items")
except Exception as e:
    print(f"✗ Error updating scavenging descriptions: {e}")

conn.commit()
conn.close()

print("\n" + "=" * 50)
print("✅ DATABASE UPDATE COMPLETE!")
print("=" * 50)
print("\nRun check_database.py to verify the changes.")
