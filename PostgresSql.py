import psycopg2
# conn = psycopg2.connect(database="", user="", password="", host="", port="")

cur = conn.cursor()

# select 
# cur.execute("SELECT * FROM membertable")
# rows = cur.fetchall()
# print(rows)

# INSERT data
# cur.execute("INSERT INTO membertable(membername, membernumber) VALUES('YES', '001')")

# creat table
# cur.execute('''CREATE TABLE membertable
#        (ID serial PRIMARY KEY NOT NULL,
#        membername TEXT NOT NULL,
#        membernumber INT NOT NULL);''')

# updata
# cur.execute("UPDATE membertable set membernumber = 002 where ID=1")

# Delete
# cur.execute("DELETE from membertable where ID=2")

conn.commit()
cur.close()



