import psycopg2
conn = psycopg2.connect(database="", user="", password="", host="", port="")

cur = conn.cursor()

# select 1
# cur.execute("SELECT * FROM membertable WHERE membername = '蔡榮富'")
# rows = cur.fetchall()
# for row in rows:
#     print(str(row))
# print(rows[0][0],rows[0][1],rows[0][2],rows[0][3])

# select 列出欄位名稱
# cur.execute("SELECT * FROM membertable WHERE membername = '蔡榮富'")
# Data = list(map(lambda x: x[0], cur.description))
# print(Data)

# INSERT data
# cur.execute("INSERT INTO membertable(membername, membernumber) VALUES('YES', '001')")

# creat table
# ID serial PRIMARY KEY NOT NULL,
# cur.execute('''CREATE TABLE membertable
#        ( 
#        memberName TEXT NOT NULL,
#        memberNumber TEXT NOT NULL UNIQUE,
#        memberAvatar TEXT NOT NULL,
#        memberTicketType TEXT NOT NULL);''')

# updata
# cur.execute("UPDATE membertable set membernumber = 002 where ID=1")

# Delete
# cur.execute("DELETE from membertable where ID=2")

conn.commit()
cur.close()