import sqlite3

# Connect to your database
conn = sqlite3.connect('game_database.db')
cursor = conn.cursor()

print("=" * 50)
print("DATABASE STRUCTURE CHECK")
print("=" * 50)

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

print(f"\n📋 Tables found: {len(tables)}")
for table in tables:
    print(f"  - {table[0]}")

print("\n" + "=" * 50)
print("DETAILED TABLE STRUCTURES")
print("=" * 50)

# Check each table's structure
for table in tables:
    table_name = table[0]
    print(f"\n📊 Table: {table_name}")
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    
    for col in columns:
        col_id, col_name, col_type, not_null, default_val, pk = col
        print(f"  - {col_name} ({col_type})", end="")
        if pk:
            print(" [PRIMARY KEY]", end="")
        if not_null:
            print(" [NOT NULL]", end="")
        if default_val:
            print(f" [DEFAULT: {default_val}]", end="")
        print()

print("\n" + "=" * 50)

conn.close()
