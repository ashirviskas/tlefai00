def patikrinti_duomenis(db, username, password):
    cur = db.cursor()
    cur.execute("SELECT * FROM User")
    for row in cur.fetchall():
        if (row[2] == username and row[3] == password):
            return row[0]
    return None

def prisijungti(db, username, session):
    session['user_id'] = str(id)
    session['logged_in'] = True
    return True

