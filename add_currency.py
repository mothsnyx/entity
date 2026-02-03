import sqlite3

conn = sqlite3.connect('game_database.db')
cursor = conn.cursor()

print("=" * 50)
print("ADDING CURRENCY TYPE TO SHOP")
print("=" * 50)

try:
    cursor.execute("ALTER TABLE shop_items ADD COLUMN currency_type TEXT DEFAULT 'bloodpoints'")
    print("✓ Added currency_type column to shop_items")
except sqlite3.OperationalError as e:
    if "duplicate column" in str(e).lower():
        print("✗ shop_items already has currency_type column")
    else:
        print(f"✗ Error: {e}")

# Set default currency type for existing items
try:
    cursor.execute("UPDATE shop_items SET currency_type = 'bloodpoints' WHERE currency_type IS NULL")
    count = cursor.rowcount
    print(f"✓ Set default currency_type for {count} items")
except Exception as e:
    print(f"✗ Error updating currency types: {e}")

conn.commit()
conn.close()

print("\n" + "=" * 50)
print("✅ CURRENCY TYPE ADDED!")
print("=" * 50)
print("\nYou can now add items with currency_type:")
print("  - 'bloodpoints' (BP)")
print("  - 'auric_cells' (AC)")
