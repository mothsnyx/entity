import sqlite3

conn = sqlite3.connect('game_database.db')
cursor = conn.cursor()

print("=" * 50)
print("CHECKING COLUMN ORDER IN DATABASE")
print("=" * 50)

tables = ['hunting_items', 'fishing_items', 'scavenging_items', 'shop_items']

for table in tables:
    print(f"\n📊 {table}:")
    cursor.execute(f"PRAGMA table_info({table})")
    columns = cursor.fetchall()
    
    for col in columns:
        col_id, col_name, col_type, not_null, default_val, pk = col
        print(f"  [{col_id}] {col_name} ({col_type})")

conn.close()

print("\n" + "=" * 50)
print("This shows the actual order of columns in your database")
print("The HTML templates need to match these positions!")
print("=" * 50)
