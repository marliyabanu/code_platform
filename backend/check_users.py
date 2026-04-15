import sqlite3
import os

DB_PATH = 'database.db'

if not os.path.exists(DB_PATH):
    print("Database not found!")
    exit()

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Check if users table exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
if not cursor.fetchone():
    print("Users table doesn't exist!")
    conn.close()
    exit()

# Get all users
cursor.execute("SELECT id, username FROM users")
users = cursor.fetchall()

if users:
    print("Existing users in database:")
    for user in users:
        print(f"  ID: {user[0]}, Username: '{user[1]}'")
else:
    print("No users found in database.")

# Check table structure
cursor.execute("PRAGMA table_info(users)")
columns = cursor.fetchall()
print("\nTable structure:")
for col in columns:
    print(f"  {col[1]} ({col[2]})")

conn.close()