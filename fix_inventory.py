"""
One-time script to find and clean up duplicate inventory entries
caused by case inconsistency (e.g. "medkit" and "Medkit" both in same inventory).

Usage:
    python fix_inventory.py              # lists all duplicates found
    python fix_inventory.py --fix        # removes the non-canonical duplicates
    python fix_inventory.py --character "Norton"   # check one character only
"""

import sqlite3
import sys

DB_PATH = "game_database.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

def find_duplicates(character_filter=None):
    """Find inventory entries that are duplicates when compared case-insensitively."""
    conn = get_connection()
    cursor = conn.cursor()

    if character_filter:
        cursor.execute("""
            SELECT character_name, item_name, COUNT(*) as qty
            FROM inventory
            WHERE LOWER(character_name) = LOWER(?)
            GROUP BY character_name, item_name
            ORDER BY character_name, item_name
        """, (character_filter,))
    else:
        cursor.execute("""
            SELECT character_name, item_name, COUNT(*) as qty
            FROM inventory
            GROUP BY character_name, item_name
            ORDER BY character_name, item_name
        """)
    all_rows = cursor.fetchall()
    conn.close()

    # Group by character + lowercase item_name to find case conflicts
    from collections import defaultdict
    grouped = defaultdict(list)
    for char, item, qty in all_rows:
        grouped[(char.lower(), item.lower())].append((char, item, qty))

    duplicates = {k: v for k, v in grouped.items() if len(v) > 1}
    return duplicates

def list_duplicates(character_filter=None):
    duplicates = find_duplicates(character_filter)
    if not duplicates:
        print("✓ No duplicate inventory entries found!")
        return

    print(f"\nFound {len(duplicates)} duplicate group(s):\n")
    print(f"{'Character':<20} {'Stored Name':<30} {'Qty'}")
    print("-" * 60)
    for (char_lower, item_lower), variants in duplicates.items():
        for char, item, qty in variants:
            marker = " ← KEEP (matches shop)" if _is_canonical(item) else " ← REMOVE"
            print(f"{char:<20} {item:<30} {qty}{marker}")
        print()

def _is_canonical(item_name):
    """Check if this item_name matches what's stored in any shop/loot table."""
    conn = get_connection()
    cursor = conn.cursor()
    for table in ("shop_items", "hunting_items", "fishing_items", "scavenging_items"):
        col = "item_name"
        cursor.execute(f"SELECT {col} FROM {table} WHERE {col} = ?", (item_name,))
        if cursor.fetchone():
            conn.close()
            return True
    conn.close()
    return False

def fix_duplicates(character_filter=None):
    """Remove the non-canonical (wrong-case) duplicate entries."""
    duplicates = find_duplicates(character_filter)
    if not duplicates:
        print("✓ No duplicates to fix!")
        return

    conn = get_connection()
    cursor = conn.cursor()
    removed = 0

    for (char_lower, item_lower), variants in duplicates.items():
        # Sort: canonical (shop-matched) names first
        canonical = [v for v in variants if _is_canonical(v[1])]
        non_canonical = [v for v in variants if not _is_canonical(v[1])]

        if not canonical:
            # No shop match for either — keep the one with most qty, remove the other
            variants_sorted = sorted(variants, key=lambda x: x[2], reverse=True)
            non_canonical = variants_sorted[1:]

        for char, item, qty in non_canonical:
            # Remove ALL rows for this character+item combination
            cursor.execute(
                "DELETE FROM inventory WHERE character_name = ? AND item_name = ?",
                (char, item)
            )
            print(f"  Removed {qty}x '{item}' from {char}'s inventory")
            removed += qty

    conn.commit()
    conn.close()
    print(f"\n✓ Done. Removed {removed} duplicate inventory row(s).")
    print("  The correct-cased versions remain untouched.")

if __name__ == "__main__":
    character_filter = None
    if "--character" in sys.argv:
        try:
            character_filter = sys.argv[sys.argv.index("--character") + 1]
            print(f"Filtering to character: {character_filter}")
        except IndexError:
            print("Usage: python fix_inventory.py --character 'CharacterName'")
            sys.exit(1)

    if "--fix" in sys.argv:
        print("Finding and removing duplicate inventory entries...\n")
        list_duplicates(character_filter)
        print("\nApplying fixes...")
        fix_duplicates(character_filter)
    else:
        list_duplicates(character_filter)
        print("\nRun with --fix to remove the duplicates.")
        print("Run with --character 'Name' to check a specific character.")
