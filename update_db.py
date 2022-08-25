import requests
import csv


def reform(text: list):
    if text[0].count('"') % 2 == 1:
        for i in range(1, len(text)):
            if '"' in text[i]:
                text[0] = ','.join(text[0:i + 1])
                del text[1: i + 1]
                break


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.160 YaBrowser/22.5.3.684 Yowser/2.5 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Language': 'ru,en;q=0.9,es;q=0.8'
}
session = requests.Session()


def update_db(con):
    html = session.get('https://minjust.gov.ru/uploaded/files/exportfsm.csv', headers=headers)

    with open("p.csv", "wb") as code:
        code.write(html.content)
        code.close()

    with open('p.csv', newline='') as f:
        reader = csv.reader(f, delimiter=';', quotechar='"')
        last_id = list(reader)[-1][0]

        cur = con.cursor()

        cur.execute('SELECT id FROM raw_book_data')
        all_id_db = [int(i[0]) for i in cur.fetchall()[1:]]
        last_id_db = max(all_id_db)

        con.close()

        flag = False
        if last_id_db != int(last_id):
            flag = True
            for i in list(reader):
                if int(i[0]) <= last_id_db:
                    print('update')
                    cur.execute('UPDATE raw_book_data SET name = "{}" WHERE id = "{}"'.format(str(i[1]), str(i[0])))
                else:
                    print('new')
                    cur.execute("INSERT INTO raw_book_data (id, name) VALUES ('{}', '{}')".format(str(i[0]), str(i[1])))
                    id = i[0]

                    raw_name = i[1].lower().split(',')

                    date = i[2] if i[2] else None

                    reform(raw_name)
                    name = raw_name[0]

                    author = raw_name[1].strip().split('автор – ') if 'автор' in raw_name else None

                    try:
                        type, title = name.split('"')[0: 2]
                        cur.execute(
                            "INSERT INTO book_data (id, name, author, date) VALUES ('{}', '{}', '{}', '{}')".format(
                                str(id),
                                title,
                                author,
                                date)
                        )
                        con.commit()
                    except Exception as e:
                        print(e)

            con.commit()
            cur.close()
            return flag
