import sqlite3
conn = sqlite3.connect("your_bot.db")
conn.execute("PRAGMA foreign_keys=OFF")

# See everything in profiles
for row in conn.execute("SELECT id, name, user_id FROM profiles ORDER BY name"):
    print(row)

# Delete a specific ghost by exact name
conn.execute("DELETE FROM profiles WHERE name = 'Fugo'")
conn.execute("DELETE FROM inventory WHERE character_name = 'Fugo'")

conn.commit()
conn.close()
