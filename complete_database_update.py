import sqlite3

# Connect to your database
conn = sqlite3.connect('game_database.db')
cursor = conn.cursor()

print("=" * 50)
print("UPDATING DATABASE STRUCTURE")
print("=" * 50)

# Add category columns
try:
    cursor.execute("ALTER TABLE shop_items ADD COLUMN category TEXT DEFAULT 'Miscellaneous'")
    print("✓ Added category to shop_items")
except sqlite3.OperationalError as e:
    if "duplicate column" in str(e).lower():
        print("✗ shop_items already has category column")
    else:
        print(f"✗ Error with shop_items: {e}")

try:
    cursor.execute("ALTER TABLE hunting_items ADD COLUMN category TEXT")
    print("✓ Added category to hunting_items")
except sqlite3.OperationalError as e:
    if "duplicate column" in str(e).lower():
        print("✗ hunting_items already has category column")
    else:
        print(f"✗ Error with hunting_items: {e}")

try:
    cursor.execute("ALTER TABLE fishing_items ADD COLUMN category TEXT")
    print("✓ Added category to fishing_items")
except sqlite3.OperationalError as e:
    if "duplicate column" in str(e).lower():
        print("✗ fishing_items already has category column")
    else:
        print(f"✗ Error with fishing_items: {e}")

try:
    cursor.execute("ALTER TABLE scavenging_items ADD COLUMN category TEXT")
    print("✓ Added category to scavenging_items")
except sqlite3.OperationalError as e:
    if "duplicate column" in str(e).lower():
        print("✗ scavenging_items already has category column")
    else:
        print(f"✗ Error with scavenging_items: {e}")

# Commit category changes
conn.commit()

print("\n" + "=" * 50)
print("ADDING DESCRIPTION COLUMNS")
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

# Commit description changes
conn.commit()

print("\n" + "=" * 50)
print("SETTING DEFAULT CATEGORIES FOR EXISTING ITEMS")
print("=" * 50)

# Set default categories for existing items that don't have one
try:
    cursor.execute("UPDATE hunting_items SET category = 'Miscellaneous' WHERE category IS NULL")
    count = cursor.rowcount
    print(f"✓ Set default category for {count} hunting items")
except Exception as e:
    print(f"✗ Error updating hunting categories: {e}")

try:
    cursor.execute("UPDATE fishing_items SET category = 'Miscellaneous' WHERE category IS NULL")
    count = cursor.rowcount
    print(f"✓ Set default category for {count} fishing items")
except Exception as e:
    print(f"✗ Error updating fishing categories: {e}")

try:
    cursor.execute("UPDATE scavenging_items SET category = 'Miscellaneous' WHERE category IS NULL")
    count = cursor.rowcount
    print(f"✓ Set default category for {count} scavenging items")
except Exception as e:
    print(f"✗ Error updating scavenging categories: {e}")

try:
    cursor.execute("UPDATE shop_items SET category = 'Miscellaneous' WHERE category IS NULL")
    count = cursor.rowcount
    print(f"✓ Set default category for {count} shop items")
except Exception as e:
    print(f"✗ Error updating shop categories: {e}")

conn.commit()

print("\n" + "=" * 50)
print("ADDING SAMPLE DESCRIPTIONS")
print("=" * 50)

# Add example descriptions to common items if they exist
try:
    # Hunting
    cursor.execute("UPDATE hunting_items SET description = 'You skillfully tracked and hunted wild game through the fog.' WHERE item_name = 'Fresh Meat' AND description IS NULL")
    cursor.execute("UPDATE hunting_items SET description = 'After a successful hunt, you claim valuable hide from your prey.' WHERE item_name = 'Animal Hide' AND description IS NULL")
    cursor.execute("UPDATE hunting_items SET description = 'Your hunt yielded useful bone fragments.' WHERE item_name = 'Bone Fragment' AND description IS NULL")
    cursor.execute("UPDATE hunting_items SET description = 'Despite your efforts, the prey escaped into the fog.' WHERE item_name IS NULL AND description IS NULL")
    print("✓ Added sample descriptions to hunting items")
except Exception as e:
    print(f"Note: Could not add hunting descriptions (items may not exist yet): {e}")

try:
    # Fishing
    cursor.execute("UPDATE fishing_items SET description = 'You cast your line into the murky waters and reel in a fresh fish!' WHERE item_name = 'Fresh Fish' AND description IS NULL")
    cursor.execute("UPDATE fishing_items SET description = 'You reeled in an old boot. Better than nothing!' WHERE item_name = 'Old Boot' AND description IS NULL")
    cursor.execute("UPDATE fishing_items SET description = 'Something ancient surfaced from the depths.' WHERE item_name = 'Strange Relic' AND description IS NULL")
    cursor.execute("UPDATE fishing_items SET description = 'The fish were not biting today.' WHERE item_name IS NULL AND description IS NULL")
    print("✓ Added sample descriptions to fishing items")
except Exception as e:
    print(f"Note: Could not add fishing descriptions (items may not exist yet): {e}")

try:
    # Scavenging
    cursor.execute("UPDATE scavenging_items SET description = 'You found useful scrap metal among the debris.' WHERE item_name = 'Scrap Metal' AND description IS NULL")
    cursor.execute("UPDATE scavenging_items SET description = 'You discovered a stash of old coins!' WHERE item_name = 'Old Coins' AND description IS NULL")
    cursor.execute("UPDATE scavenging_items SET description = 'You scavenged medical supplies from an abandoned building.' WHERE item_name = 'Medical Supplies' AND description IS NULL")
    cursor.execute("UPDATE scavenging_items SET description = 'Your search turned up empty.' WHERE item_name IS NULL AND description IS NULL")
    print("✓ Added sample descriptions to scavenging items")
except Exception as e:
    print(f"Note: Could not add scavenging descriptions (items may not exist yet): {e}")

conn.commit()
conn.close()

print("\n" + "=" * 50)
print("✅ DATABASE UPDATE COMPLETE!")
print("=" * 50)
print("\nYour database now has:")
print("  - category columns in all minigame tables")
print("  - description columns in all minigame tables")
print("  - default categories set for existing items")
print("  - sample descriptions for common items")
print("\nYou can now use the dashboard to manage categories and descriptions!")
