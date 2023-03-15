import sqlite3

conn = sqlite3.connect('humidtemps.db') 
cur = conn.cursor()

try:
    cur.execute('''
                CREATE TABLE IF NOT EXISTS humidtemps
                ([ID] INTEGER PRIMARY KEY AUTOINCREMENT,
                [DATETIME] TEXT,
                [TEMPERATURE] REAL,
                [HUMIDITY] REAL
                )
                ''')
except sqlite3.Error as e:
    print(f'Could not create ! {e} ')
finally:
    conn.commit()
