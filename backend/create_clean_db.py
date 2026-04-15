import sqlite3
import os

DB_PATH = 'database.db'

# Delete existing database if it exists
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)
    print("✅ Old database deleted")

# Create new database with correct schema
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Create users table with all columns
cursor.execute('''
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        solved_problems TEXT DEFAULT '[]',
        submissions INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

# Create submissions table
cursor.execute('''
    CREATE TABLE submissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        problem_id INTEGER NOT NULL,
        code TEXT NOT NULL,
        status TEXT DEFAULT 'accepted',
        result TEXT,
        submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
''')

# Create reviews table
cursor.execute('''
    CREATE TABLE reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        submission_id INTEGER NOT NULL,
        rating INTEGER DEFAULT 0,
        comment TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (submission_id) REFERENCES submissions(id)
    )
''')

# Insert a test user to verify (optional - you can delete this later)
cursor.execute('''
    INSERT INTO users (username, password, solved_problems, submissions)
    VALUES (?, ?, ?, ?)
''', ('test_user', 'test123', '[]', 0))

conn.commit()
conn.close()

print("✅ Fresh database created with correct schema!")
print("   - users table has all required columns")
print("   - Test user 'test_user' created (password: test123)")
print("\nNow restart your Flask app and sign up with a new username!")