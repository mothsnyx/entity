import sqlite3

conn = sqlite3.connect('game_database.db')
cursor = conn.cursor()

print("=" * 50)
print("ADDING EMBEDS TABLE")
print("=" * 50)

# Create embeds table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS embeds (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        title TEXT,
        description TEXT,
        color TEXT DEFAULT '000000',
        footer_text TEXT,
        image_url TEXT,
        thumbnail_url TEXT,
        channel_id TEXT,
        message_id TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

print("✓ Created embeds table")

conn.commit()
conn.close()

print("\n" + "=" * 50)
print("✅ EMBEDS TABLE CREATED!")
print("=" * 50)
print("\nYou can now:")
print("  - Create embeds in the dashboard")
print("  - Send them to Discord channels")
print("  - Edit existing embeds")
