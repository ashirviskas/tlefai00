import MySQLdb

print("Will connect")

password_ = open("database.txt", "r").readline()
db = MySQLdb.connect(host="159.203.142.248", user="root", passwd=password_, db="tlefdatabase")
print("Connected")

cur = db.cursor()
print("Cursor")

cur.execute("SELECT * FROM User")
print("Cursor executed")

for row in cur.fetchall():
    print(row[2], " ", row[3])