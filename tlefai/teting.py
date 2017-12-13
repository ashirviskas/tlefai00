import MySQLdb
from time import gmtime, strftime
# strftime("%Y-%m-%d %H:%M:%S", gmtime())
#
password_ = open("database.txt", "r").readline()[:-1]
db = MySQLdb.connect(host="159.203.142.248", user="root", passwd=password_, db="tlefdatabase")
# print("Connected")
#
# cur = db.cursor()
# print("Cursor")
#
# cur.execute("SELECT * FROM User")
# print("Cursor executed")
#
# for row in cur.fetchall():
#     print(row[2], " ", row[3])
from tlefai import ServerPilot_valdiklis

client_id = "cid_dgyKekddFH2yZTMt"
api_key = "IdqKGa82Q1W4nehC7FXUe6e5PdWp03LUyQRadOdTcoo"
session = {}
session['user_id'] = 1


ServerPilot_valdiklis.siusti_parinktis_i_API(session, db)
