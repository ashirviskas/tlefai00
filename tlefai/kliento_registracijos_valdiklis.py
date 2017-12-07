from time import gmtime, strftime
def uzregistruoti_vartotoja(db, username, email, password):
    cur = db.cursor()
    try:
        cur.execute("""INSERT INTO User (username, email, password, date_of_signup) VALUES (%s,%s,%s,%s)""",(username, email, password, strftime("%Y-%m-%d %H:%M:%S", gmtime())))
        db.commit()
    except:
        print("Failed adding to database")
        return False
    return True
