import sqlite3


# Connect to the database
conn = sqlite3.connect("data/tasks.db")
cursor = conn.cursor()

# Create tasks table
# cursor.execute('''
# CREATE TABLE IF NOT EXISTS tasks (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     task TEXT NOT NULL,
#     time TEXT NOT NULL,
#     completed INTEGER DEFAULT 0
# )
# ''')
# conn.commit()

 
# Add a task
def add_task(task, time):
    cursor.execute('''
    INSERT INTO tasks (task, time)
    VALUES (?, ?)
    ''', (task, time))
    conn.commit()

# View all tasks
def view_tasks():
    cursor.execute('SELECT * FROM tasks')
    return cursor.fetchall()

# Mark a task as completed
def mark_task_completed(task_id):
    cursor.execute('''
    UPDATE tasks
    SET completed = 1
    WHERE id = ?
    ''', (task_id,))
    conn.commit()

