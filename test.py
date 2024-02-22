import sqlite3

conn = sqlite3.connect('res/saves/test1.db')
cur = conn.cursor()

test = cur.execute('select * from entities').fetchall()

print(test.__len__())
print(test)
