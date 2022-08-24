from docxtpl import DocxTemplate
import docx
from datetime import date


def make_template(book_list, dir_name, name1, name2, name3, id):
    doc = DocxTemplate("act.docx")
    context = {'ФИО_руководителя': dir_name, 'ФИО1': name1, 'ФИО2': name2, 'ФИО3': name3, 'дата': date.today()}
    doc.render(context)
    doc.save(f"act-final{str(id)}.docx")

    doc = docx.Document(f"act-final{str(id)}.docx")
    table = doc.add_table(rows=2, cols=len(book_list))

    for j in range(len(book_list)):
        cell = table.cell(j, 0)
        cell.text = book_list[j][0]
        cell = table.cell(j, 1)
        cell.text = book_list[j][1]

    doc.save(f"act-final{str(id)}.docx")



make_template('A11', 'B22', 'C333', 'B444', '123456', [['1', 'book1'], ['2', 'book2']])
