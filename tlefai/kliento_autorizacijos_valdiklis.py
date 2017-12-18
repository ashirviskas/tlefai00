def patikrinti_duomenis(db, username, password):
    cur = db.cursor()
    cur.execute("SELECT * FROM User")
    for row in cur.fetchall():
        if (row[2] == username and row[3] == password):
            return row[0]
    return None

def prisijungti(db, username, session):
    cur = db.cursor()
    user_id = 0
    cur.execute("SELECT * FROM User")
    for row in cur.fetchall():
        if (row[2] == username):
            user_id = row[0]
            session['usertypeid'] = row[5]
    session['user_id'] = user_id
    session['logged_in'] = True
    return True

