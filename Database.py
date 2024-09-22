import sqlite3

# สร้างและเชื่อมต่อกับฐานข้อมูล
conn = sqlite3.connect('game_stats.db')
cursor = conn.cursor()

# สร้างตารางสำหรับผู้ใช้
cursor.execute('''CREATE TABLE IF NOT EXISTS users
                  (username TEXT PRIMARY KEY, password TEXT, score INTEGER DEFAULT 0)''')

def register_user(username, password):
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
    except sqlite3.IntegrityError:
        return False
    return True

def login_user(username, password):
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    return cursor.fetchone() is not None

def update_score(username, score):
    cursor.execute("UPDATE users SET score = score + ? WHERE username = ?", (score, username))
    conn.commit()

# ปิดการเชื่อมต่อเมื่อเสร็จสิ้น
def close_connection():
    conn.close()
