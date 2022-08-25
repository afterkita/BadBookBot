import psycopg2

con = psycopg2.connect(
    database="d7n40s85iqs755",
    user="ktbrujggxtqcwa",
    password="3506d8f2610207a197f74994b13821ba004f2ebd8eb71b7db56a4b14b83c838a",
    host="ec2-99-81-16-126.eu-west-1.compute.amazonaws.com",
    port="5432"
)


def make_user(id, name):
    global con

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



def get_book(title: str):
    global con
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


def get_books():
    global con
    try:
        cur = con.cursor()

        cur.execute(
            "SELECT name FROM book_data"
        )
        names = set([i[0] for i in cur.fetchall()])
        return names

    except Exception:
        return set()

def get_users():
    global con

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
