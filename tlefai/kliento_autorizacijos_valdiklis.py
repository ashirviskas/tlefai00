import MySQLdb

def patikrinti_duomenis(db, username, password):
    cur = db.cursor()
    cur.execute("SELECT * FROM User")
    for row in cur.fetchall():
        if (row[2] == username and row[3] == password):
            return True
    return False

def prisijungti(db, username):
    return 'Prijungto vartotojo puslapis, vartotojas: ' + username

