import sqlite3

conn = sqlite3.connect('game_database.db')
cursor = conn.cursor()

print("=" * 50)
print("ADDING REACTION ROLES TABLE")
print("=" * 50)

# Create reaction_roles table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS reaction_roles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        message_id TEXT NOT NULL,
        emoji TEXT NOT NULL,
        role_id TEXT NOT NULL,
        UNIQUE(message_id, emoji)
    )
''')

print("✓ Created reaction_roles table")

conn.commit()
conn.close()

print("\n" + "=" * 50)
print("✅ REACTION ROLES TABLE CREATED!")
print("=" * 50)
print("\nYou can now:")
print("  - Create embeds with reaction roles")
print("  - Users get roles by clicking emojis")
print("  - Roles removed when emoji is removed")
