import sqlite3
from .Test_Data.test_data import load_data
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
    FOREIGN KEY ('user_id') REFERENCES 'user'('id') ON DELETE CASCADE
);
"""

CHAT = """
CREATE TABLE 'chat' (
    'id' INTEGER NOT NULL,
    'session_id' INTEGER NOT NULL,
    'role' TEXT NOT NULL,
    'content' TEXT NOT NULL,
    PRIMARY KEY ('id'),
    FOREIGN KEY ('session_id') REFERENCES 'session'('id') ON DELETE CASCADE
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
    FOREIGN KEY ('session_id') REFERENCES 'session'('id') ON DELETE CASCADE
);
"""

FILE = """
CREATE TABLE 'file' (
    'id' INTEGER NOT NULL,
    'filename' TEXT NOT NULL,
    'category' TEXT NOT NULL,
    'session_id' INTEGER NOT NULL,
    'pinecone' TEXT,
    PRIMARY KEY ('id'),
    FOREIGN KEY ('session_id') REFERENCES 'session'('id') ON DELETE CASCADE
);
"""

drop_statements = [
    "DROP TABLE IF EXISTS file;",
    "DROP TABLE IF EXISTS repository;",
    "DROP TABLE IF EXISTS chat;",
    "DROP TABLE IF EXISTS session;",
    "DROP TABLE IF EXISTS user;"
]

USER_DATA="""
INSERT INTO user (id, email, password, AZURE_PERSONAL_ACCESS_TOKEN) VALUES
(1, 'testuser@example.com', 'testpassword', 'test_token');
"""
SESSION_DATA="""
INSERT INTO session (id, user_id, name, organization, project, project_name) VALUES
(1, 1, 'Test Session 1', 'Test Organization', 'Test Project 1', 'Test Project Name 1'),
(2, 1, 'Test Session 2', 'Test Organization', 'Test Project 2', 'Test Project Name 2');
"""
CHAT_DATA="""
INSERT INTO chat (id, session_id, role, content) VALUES
(1, 1, 'user', 'Hello, this is the first chat message in session 1'),
(2, 1, 'ai', 'Hi there! How can I assist you today?'),
(3, 1, 'user', 'I need help with my project.'),
(4, 2, 'user', 'Hello, this is the first chat message in session 2'),
(5, 2, 'ai', 'Hello! How can I help you with your project in session 2?'),
(6, 2, 'user', 'I have some issues with my files.');
"""
REPOSITORIES_DATA="""
INSERT INTO repository (id, session_id, name, repository_id, url) VALUES
(1, 1, 'Repo 1', 'repo1_id', 'http://example.com/repo1'),
(2, 2, 'Repo 2', 'repo2_id', 'http://example.com/repo2');
"""
FILES_DATA="""
INSERT INTO file (id, filename, category, session_id) VALUES
(1, 'file1.py', 'code', 1),
(2, 'file2.docx', 'documentation', 1),
(3, 'file3.cs', 'code', 2),
(4, 'file4.pdf', 'documentation', 2);
"""

con = sqlite3.connect('./database/sqlite/chatbot.db')
cur = con.cursor()

# Create tables
def create():
    try:
        for statement in drop_statements:
            cur.execute(statement)
        con.commit()
        cur.execute(USER)
        cur.execute(SESSION)
        cur.execute(CHAT)
        cur.execute(REPOSITORY)
        cur.execute(FILE)
        con.commit()
        print("Tables created successfully.")
        cur.execute(USER_DATA)
        cur.execute(SESSION_DATA)
        cur.execute(CHAT_DATA)
        cur.execute(REPOSITORIES_DATA)
        cur.execute(FILES_DATA)
        con.commit()
        print("loaded sample data")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        con.close()