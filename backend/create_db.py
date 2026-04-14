import sqlite3

print("Creating database...")

# Connect to database
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Drop existing tables if they exist
cursor.execute('DROP TABLE IF EXISTS users')
cursor.execute('DROP TABLE IF EXISTS submissions')

print("✓ Old tables removed")

# Create users table with email column
cursor.execute('''
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    created_at TEXT NOT NULL
)
''')

# Create submissions table
cursor.execute('''
CREATE TABLE submissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    problem_id INTEGER NOT NULL,
    code TEXT NOT NULL,
    language TEXT NOT NULL,
    status TEXT NOT NULL,
    submitted_at TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id)
)
''')

conn.commit()
conn.close()

print("✓ Database created successfully!")
print("✓ Users table has columns: id, username, email, password, created_at")
print("✓ Submissions table created")