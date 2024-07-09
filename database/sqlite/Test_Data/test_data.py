import sqlite3

con = sqlite3.connect('./database/sqlite/chatbot.db')
cur = con.cursor()
USER="""
INSERT INTO user (id, email, password, AZURE_PERSONAL_ACCESS_TOKEN) VALUES
(1, 'testuser@example.com', 'testpassword', 'test_token');
"""
SESSION="""
INSERT INTO session (id, user_id, name, organization, project, project_name) VALUES
(1, 1, 'Test Session 1', 'Test Organization', 'Test Project 1', 'Test Project Name 1'),
(2, 1, 'Test Session 2', 'Test Organization', 'Test Project 2', 'Test Project Name 2');
"""
CHAT="""
INSERT INTO chat (id, session_id, role, content) VALUES
(1, 1, 'user', 'Hello, this is the first chat message in session 1'),
(2, 1, 'bot', 'Hi there! How can I assist you today?'),
(3, 1, 'user', 'I need help with my project.'),
(4, 2, 'user', 'Hello, this is the first chat message in session 2'),
(5, 2, 'bot', 'Hello! How can I help you with your project in session 2?'),
(6, 2, 'user', 'I have some issues with my files.');
"""
REPOSITORIES="""
INSERT INTO repository (id, session_id, name, repository_id, url) VALUES
(1, 1, 'Repo 1', 'repo1_id', 'http://example.com/repo1'),
(2, 2, 'Repo 2', 'repo2_id', 'http://example.com/repo2');
"""
FILES="""
INSERT INTO file (id, filename, category, session_id) VALUES
(1, 'file1.py', 'code', 1),
(2, 'file2.docx', 'documentation', 1),
(3, 'file3.cs', 'code', 2),
(4, 'file4.pdf', 'documentation', 2);

"""
# Create tables
def create():
    try:
        cur.execute(USER)
        cur.execute(SESSION)
        cur.execute(CHAT)
        cur.execute(REPOSITORIES)
        cur.execute(FILES)
        con.commit()
        print("Data entered Successfully")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        con.close()

create()