import datetime
from openpyxl import load_workbook
import json

from io import BytesIO
from reportlab.pdfgen.canvas import Canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import black, red, blue, green

from PyPDF2 import PdfReader, PdfWriter

import arabic_reshaper
import bidi.algorithm 

import os


#
color_dict = {"Black":black,"Red":red,"Blue":blue,"Green":green}


#
def load_data(data_file_path):
        wb = load_workbook(data_file_path)
        ws = wb.active
        return ws.values


#
def load_coordinate(coord_file_path):
    with open(coord_file_path, "r") as f:
        c = json.load(f)
    return c


#
def fill(data,pos,font_setting,template_file,template_file_page_num,output_file_name):
    try:
        packet = BytesIO()
        #
        if font_setting[0] == "ARIAL":
            file_dir = os.path.dirname(__file__)
            file_name = os.path.join(file_dir, "arial.ttf")

            pdfmetrics.registerFont(TTFont("ARIAL", file_name))

        canvas = Canvas(packet)

        canvas.setFillColor(color_dict[font_setting[2]])

        canvas.setFont(font_setting[0], font_setting[1])

        if font_setting[3] == "Right":
            drawfunc = canvas.drawRightString
        else:
            drawfunc = canvas.drawString

        for i,value in enumerate(data):
            if isinstance(value,datetime.datetime):
                # if time != 0
                if value.time() != datetime.datetime(2000, 1, 1, 0, 0, 0).time():
                    value = value
                else:
                    value = value.date()
            #
            value = arabic_reshaper.reshape(str(value))
            value = bidi.algorithm.get_display(value)
            
            drawfunc(pos[i][0], pos[i][1], value)
            
        canvas.save()
        packet.seek(0)

        _merge(packet,template_file,template_file_page_num,output_file_name)

    except Exception as e:
        print(type(e))
        return e


def _merge(packet,template_file,template_file_page_num,output_file_name):
    data_pdf = PdfReader(packet)

    template_pdf = PdfReader(open(template_file,"rb")) 

    total_template_pdf_pages = len(template_pdf.pages)

    output_writer = PdfWriter()

    for i in range(total_template_pdf_pages):
        page = template_pdf.pages[i]
        
        if i == template_file_page_num:
            page.merge_page(data_pdf.pages[0])

        output_writer.add_page(page)

    with open(output_file_name,"wb") as f:
        output_writer.write(f)







#
def disable_children_widgets(parent):
    for child in parent.winfo_children():
        wtype = child.winfo_class()
        if wtype not in ('Frame','Labelframe','TFrame','TLabelframe'):
            child.configure(state='disable')
        else:
            disable_children_widgets(child)

def enable_children_widgets(parent):
    for child in parent.winfo_children():
        wtype = child.winfo_class()
        if wtype not in ('Frame','Labelframe','TFrame','TLabelframe'):
            child.configure(state='normal')
        else:
            enable_children_widgets(child)