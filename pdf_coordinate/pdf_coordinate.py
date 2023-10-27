import fitz
from PIL import Image, ImageTk
import tkinter as tk
import tkinter.ttk as ttk
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter.simpledialog import askinteger
import os
import json

import gettext




###########################################################################################################

global_data = {
   "root":None,
   "image_window":None,
   "left_frame":None,
   "right_frame":None,
   "pdf_file_name":"",
   "pdf_file_page_num":0,
   "pdf_image_height":0,

   "coord_txt":None,
   "marker_count":1,
   
}

marker_list = []

marker_coord_list = []


###########################################################################################################
# logic

def _convert_pdf_to_image(file_name: str):
    doc = fitz.open(filename=file_name)

    page_num = _get_page_num(doc)
    if page_num != None:
        image = _get_image(doc,page_num)
        return image

def _get_page_num(doc):
    page_count = doc.page_count
    page_num = askinteger(_("Select Page Number"),_("Please enter the page number: (1 ... {})").format(page_count))
    global_data["pdf_file_page_num"] = page_num

    if page_num != None:
        if page_num <= 0:
            page_num = 0
        elif 0 < page_num and page_num <= page_count:
            page_num = page_num - 1
        else:
            page_num = page_count - 1
    
        return page_num

def _get_image(doc,page_num):
    page = doc.load_page(page_num)
    pix = page.get_pixmap()
    
    mode = "RGBA" if pix.alpha else "RGB"
    image = Image.frombytes(mode, [pix.width, pix.height], pix.samples)
    return image


#
def _add_coord(coord):
    marker_coord_list.append(coord)

def _update_coord_txt():
    coord_txt = global_data["coord_txt"]

    coord_txt.config(state=tk.NORMAL)
    coord_txt.delete(1.0,tk.END)
    if marker_coord_list:
        text = ""
        for i,v in enumerate(marker_coord_list,1):
            text += f"{i}: {v} \n"
    else:
        text = ""
    coord_txt.insert(tk.END, text)
    coord_txt.config(state=tk.DISABLED)

def _delete_last_coord():
    marker_coord_list.pop()

def _delete_all_coord():
    marker_coord_list.clear()





###########################################################################################################
# event handler

def on_about_btn_pressed():
   root = global_data["root"]

   about_window = tk.Toplevel(root)
   about_window.title("About")
   about_window.geometry("400x200")
   about_window.resizable(0,0)
   about_window.rowconfigure(0,weight=1)
   about_window.columnconfigure(0,weight=1)
   center_window(about_window)
   #
   about_window_frm = ttk.Frame(about_window)
   about_window_frm.grid()
   #
   txt = """ 
   Tkinter
   PyMuPDF
   ______

   ver 0.1
   https://github.com/sapy22
   """
   about_text = tk.Text(about_window_frm,height=9,width=40)
   about_text.grid(row=0,column=0)
   about_text.tag_configure('tag-center', justify='center')
   about_text.insert("1.0",txt,"tag-center")
   about_text["state"] = "disable"

   ttk.Button(about_window_frm, text="Exit",command=about_window.destroy).grid(row=1,column=0,pady=10)
   #
   about_window.grab_set()


def on_load_pdf_btn_pressed():
    pdf_file_path = askopenfilename(filetypes=[("PDF Files", "*.pdf")])

    if pdf_file_path and not pdf_file_path.endswith(".pdf"):
        tk.messagebox.showerror(_("Error"),_("Please select PDF files only"))
        pdf_file_path = ""

    if not pdf_file_path:
        return
    
    image = _convert_pdf_to_image(pdf_file_path)

    if image:
        tkimg = ImageTk.PhotoImage(image)
        global_data["pdf_image"] = tkimg
        setup_image_window()
        #
        global_data["pdf_file_name"] = os.path.basename(pdf_file_path).split(".")[0]
        global_data["pdf_image_height"] = tkimg.height()

    # init after reload
    if marker_coord_list:
        marker_coord_list.clear()
        global_data["marker_count"] = 1

#
def on_delete_last_btn_pressed():
    if marker_list and marker_coord_list:
        if _confirm_dialog(_("Delete Last")):
            marker, marker_num = marker_list.pop()

            marker.destroy()
            marker_num.destroy()
            global_data["marker_count"] -= 1

            _delete_last_coord()
            _update_coord_txt()
    else:
        tk.messagebox.showerror(_("Error"), _("Coord list is empty"),parent=global_data["image_window"])

def on_delete_all_btn_pressed():
    if marker_list and marker_coord_list:
        if _confirm_dialog(_("Delete All")):
            for marker, marker_num in marker_list:
                marker.destroy()
                marker_num.destroy()

            global_data["marker_count"] = 1

            _delete_all_coord()
            _update_coord_txt()

    else:
        tk.messagebox.showerror(_("Error"), _("Coord list is empty"),parent=global_data["image_window"])


def on_save_btn_pressed():
    if marker_coord_list:
        if _confirm_dialog(_("Save")):
            pdf_file_name = global_data["pdf_file_name"]
            pdf_file_page_num = str(global_data["pdf_file_page_num"])

            save_file_path = asksaveasfilename(
                initialfile=pdf_file_name + "_coords_page_" + pdf_file_page_num,
                defaultextension=".txt",
                filetypes=[("Text Files", "*.txt")],
            )
            if not save_file_path:
                return

            with open(save_file_path, mode="w") as output_file:
                json.dump(marker_coord_list, output_file)
            
    else:
        tk.messagebox.showerror(_("Error"), _("Coord list is empty"),parent=global_data["image_window"])


def on_quit_btn_pressed():
    if _confirm_dialog(_("Quit")):
        global_data["root"].destroy()


def on_image_lbl_lmb_pressed(e):
    setup_marker(e)


def _confirm_dialog(m):
    return tk.messagebox.askyesno(_('Confirmation'),_('Are you sure you want to {}?').format(m),parent=global_data["image_window"])

###########################################################################################################################
# gui

def setup_root():
   root = tk.Tk()
   root.title("pdf_coordinate")
   root.geometry("300x150")
   root.resizable(0,0)
   root.rowconfigure(0,weight=1)
   root.columnconfigure(0,weight=1)
   global_data["root"] = root


def setup_menu_bar():
   root = global_data["root"]

   menu_bar = tk.Menu()

   help_menu = tk.Menu(menu_bar, tearoff=0)

   help_menu.add_command(label="About", command=on_about_btn_pressed)

   menu_bar.add_cascade(label="Help", menu=help_menu)

   root.config(menu=menu_bar)


def setup_load_window():
    root = global_data["root"]
    main_frame = ttk.Frame(root)
    main_frame.grid(row=0,column=0)
    
    pad_option = {"padx":10,"pady":10,"ipadx":10,"ipady":10}

    ttk.Button(main_frame,text=_("Load PDF File"),command=on_load_pdf_btn_pressed).grid(row=0,column=0,**pad_option)


def setup_image_window():
    root = global_data["root"]
    image_window = tk.Toplevel(root)
    image_window.title("pdf_coordinate")
    image_window.resizable(0,0)
    image_window.rowconfigure(0,weight=1)
    image_window.columnconfigure(0,weight=1)
    global_data["image_window"] = image_window
    #
    setup_frames()
    #
    setup_widgets()
    #
    center_window(image_window)
    image_window.grab_set()


def setup_frames():
   image_window = global_data["image_window"]
   main_frame = ttk.Frame(image_window)
   main_frame.grid(row=0,column=0)

   left_frame = ttk.Frame(main_frame)
   left_frame.grid(row=0,column=0,padx=10)
   global_data["left_frame"] = left_frame

   right_frame = ttk.Frame(main_frame)
   right_frame.grid(row=0,column=1,padx=10)
   global_data["right_frame"] = right_frame


def setup_widgets():
    left_frame = global_data["left_frame"]
    right_frame = global_data["right_frame"]
   
    pad_option = {"padx":10,"pady":10,"ipadx":10,"ipady":10}

    #
    ttk.Button(left_frame,text=_("Delete Last"),command=on_delete_last_btn_pressed).grid(row=1,column=0,**pad_option)

    #
    ttk.Button(left_frame,text=_("Delete All"),command=on_delete_all_btn_pressed).grid(row=2,column=0,**pad_option)
    
    # coord
    coord_txt = tk.Text(left_frame,height = 20, width = 15,state=tk.DISABLED)
    coord_txt.grid(row=3,column=0,pady=10)
    global_data["coord_txt"] = coord_txt

    # y inverse
    y_inverse_chk_value = tk.IntVar(value=1)
    ttk.Checkbutton(left_frame,text="Y-inverce",variable=y_inverse_chk_value).grid(row=4,column=0,**pad_option)
    global_data["y_inverse_chk_value"] = y_inverse_chk_value

    #
    ttk.Button(left_frame,text=_("Save"),command=on_save_btn_pressed).grid(row=5,column=0,**pad_option)
    
    #
    ttk.Button(left_frame,text=_("Quit"),command=on_quit_btn_pressed).grid(row=6,column=0,**pad_option)

    # image
    img = global_data["pdf_image"]
    image_lbl = ttk.Label(right_frame,image=img)
    image_lbl.grid()
    image_lbl.bind("<ButtonPress-1>", lambda e: on_image_lbl_lmb_pressed(e))


def setup_marker(event):
    right_frame = global_data["right_frame"]
    marker_count = global_data["marker_count"]
    y_inverse_chk_value = global_data["y_inverse_chk_value"]
    
    marker = ttk.Label(right_frame,text="x")
    marker_num = ttk.Label(right_frame,text=f"{marker_count}",foreground="red")
    
    x = event.x
    y = event.y

    marker.place(x=x-8,y=y-16)
    marker_num.place(x=x+8,y=y-16)

    marker_list.append((marker,marker_num))
    global_data["marker_count"] += 1
    
    if y_inverse_chk_value.get():
        y = global_data["pdf_image_height"] - y
    _add_coord([x,y])
    _update_coord_txt()


def center_window(window):
    window.withdraw() # hide window
    window.update() # force update 
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    window_width = window.winfo_width()
    window_height = window.winfo_height()
    x = int((screen_width - window_width) / 2)
    y = int((screen_height - window_height) / 2)
    window.geometry(f"+{x}+{y}")
    window.deiconify() # show window


############################################################


def main():
    setup_root()
    #
    setup_menu_bar()
    #
    setup_load_window()
    #
    root = global_data["root"]
    center_window(root)
    #
    root.mainloop()





if __name__ == '__main__':

    lang = "EN"

    if lang == "AR":
        ar = gettext.translation('pdf_coordinate', localedir='locale', languages=['ar'])
        ar.install()
        _ = ar.gettext
    else:
        _ = gettext.gettext

     


    main()