import sqlite3
import os

DB_PATH = 'database.db'

def fix_database():
    if not os.path.exists(DB_PATH):
        print("Database not found. Please run the app first.")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check existing columns
    cursor.execute("PRAGMA table_info(users)")
    columns = [column[1] for column in cursor.fetchall()]
    
    print(f"Current columns: {columns}")
    
    # Add missing columns one by one
    if 'solved_problems' not in columns:
        print("Adding solved_problems column...")
        cursor.execute("ALTER TABLE users ADD COLUMN solved_problems TEXT DEFAULT '[]'")
        print("✓ solved_problems column added")
    else:
        print("✓ solved_problems column already exists")
    
    if 'submissions' not in columns:
        print("Adding submissions column...")
        cursor.execute("ALTER TABLE users ADD COLUMN submissions INTEGER DEFAULT 0")
        print("✓ submissions column added")
    else:
        print("✓ submissions column already exists")
    
    conn.commit()
    conn.close()
    
    print("\n✅ Database fixed successfully!")
    print("Now restart your Flask app.")

if __name__ == '__main__':
    fix_database()