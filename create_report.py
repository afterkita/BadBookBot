from docxtpl import DocxTemplate
from datetime import date


def make_template_report(main_name, adress, number, mail, name_material, author_material,id):
    doc = DocxTemplate("report.docx")
    context = {'ФИО': main_name, 'address': adress, 'number': number,'mail':mail,'НАЗВАНИЕ':"\"{}\"".format(name_material),'ФИО_автор':author_material,'date':date.today()}
    doc.render(context)
    doc.save(f"report-result{id}.docx")

    return f"report-result{id}.docx"

