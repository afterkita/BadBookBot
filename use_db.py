def make_user(id, name, con):
    try:
        cur = con.cursor()

        cur.execute(
            "INSERT INTO users (ID, NAME) VALUES ('{}', '{}')".format(str(id), str(name))
        )

        con.commit()
        con.close()

    except Exception:
        con.commit()
        con.close()



def get_book(title: str, con):
    try:
        cur = con.cursor()
        cur.execute(
            "SELECT name FROM raw_book_data"
        )
        name = [i[0] for i in cur.fetchall() if title.lower() in i[0].lower()]
        if name:
            return name[0]
        return None

    except Exception:
        return None


def get_books(con):
    try:
        cur = con.cursor()

        cur.execute(
            "SELECT name FROM book_data"
        )
        names = set([i[0] for i in cur.fetchall()])
        return names

    except Exception:
        return set()

def get_users(con):
    try:
        cur = con.cursor()

        cur.execute("SELECT id FROM users")

        return [i[0] for i in cur.fetchall()]

    except Exception as e:
        print(e)


def get_my_books(file_path: str):
    with open(file_path, "r", encoding='UTF-8') as file:
        text = file.read().split()
        file.close()
        return set([i.lower() for i in text])