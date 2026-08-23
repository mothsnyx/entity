"""
One-time cleanup script for the Mutated Piranha / Alligator Fish style bugs.

What it does:
1. Trims stray whitespace from item_name in hunting_items, fishing_items,
   scavenging_items, shop_items, and inventory.
2. Normalises category in hunting_items, fishing_items, scavenging_items,
   shop_items onto the canonical set (Consumables, Tools, Collectibles,
   Miscellaneous, Cosmetics, Pets, Shelter, NSFW), fixing case/whitespace
   mismatches like "consumables" or "Consumables ".
3. Merges duplicate inventory rows that only differed by whitespace/case in
   item_name (e.g. "Mutated Piranha" vs "Mutated Piranha ") by rewriting them
   all to the same trimmed value, so /inventory, /sell, and /use agree again.

Run this ONCE after deploying the code fix, from the same directory as your
game_database.db (or pass the path as an argument):

    python3 fix_item_data.py [path/to/game_database.db]

It prints exactly what it changes. Make a backup of the .db file before
running, just in case:

    cp game_database.db game_database.db.bak
"""

import sqlite3
import sys

from database import Database


def main(db_path):
    db = Database.__new__(Database)  # only need normalise/normalise_category, not __init__
    conn = sqlite3.connect(db_path)
    conn.create_function("LOWER", 1, lambda x: x.lower() if x else None)
    cursor = conn.cursor()

    item_tables = ["hunting_items", "fishing_items", "scavenging_items", "shop_items"]
    total_changes = 0

    # --- 1 & 2: fix item_name whitespace and category on the definition tables ---
    for table in item_tables:
        cursor.execute(f"SELECT id, item_name, category FROM {table}")
        rows = cursor.fetchall()
        for row_id, item_name, category in rows:
            new_name = item_name.strip() if item_name else item_name
            new_category = db.normalise_category(category) if table != "shop_items" or category else category
            if table == "shop_items":
                new_category = db.normalise_category(category)

            if new_name != item_name or new_category != category:
                cursor.execute(
                    f"UPDATE {table} SET item_name = ?, category = ? WHERE id = ?",
                    (new_name, new_category, row_id),
                )
                total_changes += 1
                print(f"[{table}] id={row_id}: "
                      f"name {item_name!r} -> {new_name!r}, "
                      f"category {category!r} -> {new_category!r}")

    # --- 3: fix whitespace in already-caught inventory rows ---
    cursor.execute("SELECT id, item_name FROM inventory")
    rows = cursor.fetchall()
    for row_id, item_name in rows:
        new_name = item_name.strip() if item_name else item_name
        if new_name != item_name:
            cursor.execute("UPDATE inventory SET item_name = ? WHERE id = ?", (new_name, row_id))
            total_changes += 1
            print(f"[inventory] id={row_id}: name {item_name!r} -> {new_name!r}")

    conn.commit()
    conn.close()

    print(f"\nDone. {total_changes} row(s) updated.")
    if total_changes == 0:
        print("No stray whitespace or category mismatches found.")


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "game_database.db"
    main(path)
