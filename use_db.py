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
            "SELECT id FROM book_data WHERE name='{}'".format(str(title).lower())
        )
        id = cur.fetchall()
        if id:

            cur.execute(
                "SELECT name FROM raw_book_data WHERE id='{}'".format(str(id)[0])
            )
            name = cur.fetchall()
            if name:
                return title
            else:
                return None
        else:
            return None
    except Exception:
        return None