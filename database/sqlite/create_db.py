import sqlite3
USER = """
CREATE TABLE 'user' (
    'id' INTEGER NOT NULL,
    'email' TEXT NOT NULL,
    'password' TEXT NOT NULL,
    'AZURE_PERSONAL_ACCESS_TOKEN' TEXT,
    PRIMARY KEY ('id'),
    UNIQUE ('email')
);
"""

SESSION = """
CREATE TABLE 'session' (
    'id' INTEGER NOT NULL,
    'user_id' INTEGER NOT NULL,
    'name' TEXT NOT NULL,
    'organization' TEXT,
    'project' TEXT,
    'project_name' TEXT,
    PRIMARY KEY ('id'),
    FOREIGN KEY ('user_id') REFERENCES 'user'('id')
);
"""

CHAT = """
CREATE TABLE 'chat' (
    'id' INTEGER NOT NULL,
    'session_id' INTEGER NOT NULL,
    'role' TEXT NOT NULL,
    'content' TEXT NOT NULL,
    PRIMARY KEY ('id'),
    FOREIGN KEY ('session_id') REFERENCES 'session'('id')
);
"""

REPOSITORY = """
CREATE TABLE 'repository' (
    'id' INTEGER NOT NULL,
    'session_id' INTEGER NOT NULL,
    'name' TEXT NOT NULL,
    'repository_id' TEXT NOT NULL,
    'url' TEXT NOT NULL,
    PRIMARY KEY ('id'),
    FOREIGN KEY ('session_id') REFERENCES 'session'('id')
);
"""

FILE = """
CREATE TABLE 'file' (
    'id' INTEGER NOT NULL,
    'filename' TEXT NOT NULL,
    'category' TEXT NOT NULL,
    FOREIGN KEY ('session_id') REFERENCES 'session'('id')
);
"""
con = sqlite3.connect('./database/sqlite/chatbot.db')
cur = con.cursor()

# Create tables
def create():
    try:
        cur.execute(USER)
        cur.execute(SESSION)
        cur.execute(CHAT)
        cur.execute(REPOSITORY)
        con.commit()
        print("Tables created successfully.")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        con.close()
