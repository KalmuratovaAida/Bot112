from io import BytesIO
import openpyxl as pyxl
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Cm


def excel(data=None):
    wb = pyxl.load_workbook('web/templates/export/template.xlsx')
    ws = wb.active
    for row in list(ws.rows):
        for c in row:
            if c.value in data:
                ws.cell(column=c.column, row=c.row+1, value=data[c.value])
    wb_bytes = pyxl.writer.excel.save_virtual_workbook(wb)
    return BytesIO(wb_bytes)


def word(data, filename=None):
    template = DocxTemplate('web/templates/export/template.docx')
    image = None
    if filename:
        image = InlineImage(template, image_descriptor=filename, width=Cm(16))
    template.render({'image': image, **data})
    file_data = BytesIO()
    template.save(file_data)
    file_data.seek(0)
    return file_data
