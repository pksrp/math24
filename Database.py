import sqlite3

def init_db():
    conn = sqlite3.connect('game24.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS scores 
                 (player TEXT, score INTEGER)''')
    conn.commit()
    conn.close()

def update_score(player, score):
    conn = sqlite3.connect('game24.db')
    c = conn.cursor()
    c.execute("SELECT score FROM scores WHERE player=?", (player,))
    result = c.fetchone()
    if result:
        c.execute("UPDATE scores SET score = score + ? WHERE player = ?", (score, player))
    else:
        c.execute("INSERT INTO scores (player, score) VALUES (?, ?)", (player, score))
    conn.commit()
    conn.close()