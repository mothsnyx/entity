#!/usr/bin/env python3
"""
Bulk Character Ownership Assignment Tool
=========================================
Use this to manually assign ownership of existing characters
"""

import sqlite3
import sys

def get_all_characters():
    """Show all characters and their current owners"""
    conn = sqlite3.connect('game_database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name, user_id FROM profiles ORDER BY name")
    results = cursor.fetchall()
    conn.close()
    
    print("\n" + "="*70)
    print("ALL CHARACTERS")
    print("="*70)
    print(f"{'Character Name':<30} {'Owner ID':<25} {'Status'}")
    print("-" * 70)
    
    owned_count = 0
    unowned_count = 0
    
    for name, user_id in results:
        if user_id is None:
            status = "❌ UNOWNED"
            unowned_count += 1
        else:
            status = "✅ OWNED"
            owned_count += 1
        print(f"{name:<30} {user_id or 'None':<25} {status}")
    
    print("-" * 70)
    print(f"Total: {len(results)} | Owned: {owned_count} | Unowned: {unowned_count}")
    print("="*70 + "\n")
    
    return unowned_count

def assign_all_to_user(user_id):
    """Assign all unowned characters to a specific user"""
    conn = sqlite3.connect('game_database.db')
    cursor = conn.cursor()
    
    # Get count before
    cursor.execute("SELECT COUNT(*) FROM profiles WHERE user_id IS NULL")
    count = cursor.fetchone()[0]
    
    if count == 0:
        print("✅ No unowned characters to assign!")
        conn.close()
        return
    
    # Confirm
    print(f"\n⚠️  You're about to assign {count} characters to user ID: {user_id}")
    confirm = input("Continue? (yes/no): ").strip().lower()
    
    if confirm != 'yes':
        print("❌ Cancelled")
        conn.close()
        return
    
    # Assign
    cursor.execute("UPDATE profiles SET user_id = ? WHERE user_id IS NULL", (str(user_id),))
    conn.commit()
    conn.close()
    
    print(f"\n✅ Successfully assigned {count} characters to user {user_id}\n")

def assign_specific(character_name, user_id):
    """Assign a specific character to a user"""
    conn = sqlite3.connect('game_database.db')
    cursor = conn.cursor()
    
    # Check if character exists
    cursor.execute("SELECT user_id FROM profiles WHERE name = ?", (character_name,))
    result = cursor.fetchone()
    
    if not result:
        print(f"❌ Character '{character_name}' not found!")
        conn.close()
        return
    
    current_owner = result[0]
    
    if current_owner:
        print(f"⚠️  '{character_name}' is already owned by {current_owner}")
        confirm = input("Reassign anyway? (yes/no): ").strip().lower()
        if confirm != 'yes':
            print("❌ Cancelled")
            conn.close()
            return
    
    # Assign
    cursor.execute("UPDATE profiles SET user_id = ? WHERE name = ?", 
                  (str(user_id), character_name))
    conn.commit()
    conn.close()
    
    print(f"✅ Assigned '{character_name}' to user {user_id}\n")

def interactive_mode():
    """Interactive assignment wizard"""
    print("\n" + "="*70)
    print("INTERACTIVE OWNERSHIP ASSIGNMENT")
    print("="*70)
    
    unowned = get_all_characters()
    
    if unowned == 0:
        print("✅ All characters are already owned!")
        return
    
    print("\nOPTIONS:")
    print("1. Assign ALL unowned characters to one user")
    print("2. Assign a specific character")
    print("3. View character list again")
    print("4. Exit")
    
    choice = input("\nYour choice (1-4): ").strip()
    
    if choice == '1':
        user_id = input("\nEnter Discord User ID to assign ALL to: ").strip()
        if user_id:
            assign_all_to_user(user_id)
    
    elif choice == '2':
        character = input("\nEnter character name: ").strip()
        user_id = input("Enter owner's Discord ID: ").strip()
        if character and user_id:
            assign_specific(character, user_id)
    
    elif choice == '3':
        get_all_characters()
        interactive_mode()  # Show menu again
    
    else:
        print("\n👋 Goodbye!\n")
        return

def main():
    """Main entry point"""
    print("\n" + "🎮 CHARACTER OWNERSHIP ASSIGNMENT TOOL 🎮".center(70))
    
    if len(sys.argv) == 1:
        # No arguments - interactive mode
        interactive_mode()
    
    elif len(sys.argv) == 2 and sys.argv[1] == 'list':
        # List all characters
        get_all_characters()
    
    elif len(sys.argv) == 3 and sys.argv[1] == 'all':
        # Assign all to user
        user_id = sys.argv[2]
        get_all_characters()
        assign_all_to_user(user_id)
    
    elif len(sys.argv) == 4 and sys.argv[1] == 'assign':
        # Assign specific character
        character = sys.argv[2]
        user_id = sys.argv[3]
        assign_specific(character, user_id)
    
    else:
        print("""
USAGE:
    python3 assign_characters.py              # Interactive mode
    python3 assign_characters.py list         # List all characters
    python3 assign_characters.py all <ID>     # Assign all to user ID
    python3 assign_characters.py assign <name> <ID>  # Assign specific character

EXAMPLES:
    python3 assign_characters.py
    python3 assign_characters.py list
    python3 assign_characters.py all 123456789012345678
    python3 assign_characters.py assign Alice 123456789012345678
        """)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Cancelled by user\n")
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
