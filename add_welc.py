import sqlite3

conn = sqlite3.connect('game_database.db')
cursor = conn.cursor()

print("=" * 50)
print("ADDING WELCOME SETTINGS TABLE")
print("=" * 50)

# Create welcome_settings table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS welcome_settings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        enabled INTEGER DEFAULT 0,
        embed_id INTEGER,
        channel_id TEXT,
        FOREIGN KEY (embed_id) REFERENCES embeds(id) ON DELETE SET NULL
    )
''')

print("✓ Created welcome_settings table")

# Insert default settings
cursor.execute("INSERT OR IGNORE INTO welcome_settings (id, enabled, embed_id, channel_id) VALUES (1, 0, NULL, NULL)")
print("✓ Added default welcome settings")

conn.commit()
conn.close()

print("\n" + "=" * 50)
print("✅ WELCOME SETTINGS TABLE CREATED!")
print("=" * 50)
print("\nYou can now:")
print("  - Enable/disable welcome messages")
print("  - Choose which embed to use")
print("  - Set welcome channel")
print("  - Use variables: {user}, {mention}, {member_count}, {server}")
