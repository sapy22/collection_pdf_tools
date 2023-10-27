import os, sys
from PyPDF2 import PdfReader, PdfWriter
import tkinter as tk
import tkinter.ttk as ttk
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter import messagebox
import threading

import gettext





############################################################################################################


global_data = {
   "root":None,
   "top_frame":None,
   "bottom_frame":None,
   "input_file_lbl_value":None,
   "output_file_lbl_value":None,
   "num_of_page_spinebox_value":None,
   "start_btn":None,
   "input_file_path":"",
   "output_file_path":"",

   "split_err":False
}


############################################################################################################
# logic

def split(input_file_path: str,output_file_path: str,num_of_page_to_split: int):
    try:
        input_dir_name = os.path.dirname(input_file_path)
        input_file_name = os.path.splitext(os.path.basename(input_file_path))[0]
        
        output_dir_name = os.path.dirname(output_file_path)
        output_file_name = os.path.splitext(os.path.basename(output_file_path))[0]

        reader = PdfReader(input_file_path)
        writer = PdfWriter()

        output_file_count = 1
        
        temp_page_count = 0
        for page in reader.pages:
            temp_page_count += 1

            # page.compress_content_streams() # hmmm
            writer.add_page(page)

            if temp_page_count == num_of_page_to_split:
                output_file = os.path.join(output_dir_name, f'{output_file_name}_{output_file_count}.pdf')
                with open(output_file, 'wb') as output:
                    writer.write(output)
                #
                output_file_count += 1
                temp_page_count = 0
                writer = PdfWriter()

        # if there is stil some pages left
        if temp_page_count:
            output_file = os.path.join(output_dir_name, f'{output_file_name}_{output_file_count}.pdf')
            with open(output_file, 'wb') as output:
                writer.write(output)
    
    except Exception as error:
        global_data["split_err"] = True
        messagebox.showerror("Error", f"{error}")
        


#################################################################################################################################
# event handler

def on_about_btn_pressed():
   root = global_data["root"]

   about_window = tk.Toplevel(root)
   about_window.title(_("About"))
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
   PyPDF2
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


def on_input_file_btn_pressed():
    input_file = askopenfilename(filetypes=[("PDF Files", "*.pdf")])

    if input_file and not input_file.endswith(".pdf"):
        messagebox.showerror(_("Error"),_("Please select PDF files only"))
        input_file = ""
        

    if not input_file:
        global_data["input_file_lbl_value"].set(_("Please select the input file"))
        global_data["input_file_path"] = ""

        return

    if len(input_file) > 40:
        t_input_file = input_file[:15]+"/ ... /"+input_file[-25:]
    else:
        t_input_file = input_file
    
    global_data["input_file_lbl_value"].set(t_input_file)

    global_data["input_file_path"] = input_file


def on_output_file_btn_pressed():
    output_file = asksaveasfilename(defaultextension=".pdf",filetypes=[("PDF Files", "*.pdf")],)

    if not output_file:
        return

    if len(output_file) > 40:
        t_output_file = output_file[:15]+"/ ... /"+output_file[-25:]
    else:
        t_output_file = output_file
    
    global_data["output_file_lbl_value"].set(t_output_file)

    global_data["output_file_path"] = output_file


def on_start_btn_pressed():
    input_file = global_data["input_file_path"]
    output_file = global_data["output_file_path"]
    num_of_page_to_split = global_data["num_of_page_spinebox_value"].get()
    
    try:
        num_of_page_to_split = int(num_of_page_to_split)
        if 0 < num_of_page_to_split <= 9999:
            if input_file and output_file:
                
                global_data["start_btn"]["state"] = "disable"

                split_progress_bar = global_data["split_progress_bar"]
                split_progress_bar.grid(row=0,column=0,pady=10)
                split_progress_bar.start()

                t = threading.Thread(target=split,args=[input_file, output_file, num_of_page_to_split])
                t.start()

                _update_split_progress(t)
                    
            else:
                messagebox.showerror(_("Error"), _("Please select the input and output file"))
        else:
            messagebox.showerror(_("Error"), _("Please enter a number between 1 and 9999"))

    except (TypeError,ValueError):
        messagebox.showerror(_("Error"), _("Please enter numbers only"))
    
def _update_split_progress(thread):
    split_progress_bar = global_data["split_progress_bar"]
    split_err = global_data["split_err"]

    if split_err:
        split_progress_bar.stop()
        split_progress_bar.grid_forget()

    if thread.is_alive():
        global_data["root"].after(500,lambda: _update_split_progress(thread))
    else:
        if not split_err:
            split_progress_bar.stop()
            split_progress_bar.grid_forget()
            messagebox.showinfo(_("Info"),_("Done"))

        global_data["start_btn"]["state"] = "normal"


###########################################################################################################################
# gui

def setup_root():
   root = tk.Tk()
   root.title("pdf_split")
   root.geometry("500x350")
   root.resizable(0,0)
   root.rowconfigure(0,weight=1)
   root.columnconfigure(0,weight=1)
   global_data["root"] = root


def setup_menu_bar():
   root = global_data["root"]

   menu_bar = tk.Menu()

   help_menu = tk.Menu(menu_bar, tearoff=0)

   help_menu.add_command(label=_("About"), command=on_about_btn_pressed)

   menu_bar.add_cascade(label=_("Help"), menu=help_menu)

   root.config(menu=menu_bar)


def setup_frames():
   root = global_data["root"]
   main_frame = ttk.Frame(root)
   main_frame.grid(row=0,column=0)

   top_frame = ttk.Frame(main_frame)
   top_frame.grid(row=0,column=0)
   global_data["top_frame"] = top_frame

   bottom_frame = ttk.Frame(main_frame)
   bottom_frame.grid(row=1,column=0)
   global_data["bottom_frame"] = bottom_frame


def setup_widgets():
    top_frame = global_data["top_frame"]
    bottom_frame = global_data["bottom_frame"]
   
    pad_option = {"padx":10,"pady":10,"ipadx":10,"ipady":10}

    # input
    input_file_lbl_value = tk.StringVar(value=_("Please select the input file"))
    ttk.Label(top_frame,textvariable=input_file_lbl_value,width=40).grid(row=0,column=0,**pad_option)
    global_data["input_file_lbl_value"] = input_file_lbl_value

    ttk.Button(top_frame,text=_("Input File"),command=on_input_file_btn_pressed).grid(row=0,column=1,**pad_option)

    # output
    output_file_lbl_value = tk.StringVar(value=_("Please select the output file"))
    ttk.Label(top_frame,textvariable=output_file_lbl_value,width=40).grid(row=1,column=0,**pad_option)
    global_data["output_file_lbl_value"] = output_file_lbl_value

    ttk.Button(top_frame,text=_("Output File"),command=on_output_file_btn_pressed).grid(row=1,column=1,**pad_option)

    # num_of_page
    num_of_page_spinebox_value = tk.StringVar(value=1)
    ttk.Label(top_frame,text=_("Select the number Of pages to split"),width=40).grid(row=2,column=0,**pad_option)
    global_data["num_of_page_spinebox_value"] = num_of_page_spinebox_value

    ttk.Spinbox(top_frame,from_=1,to=9999,textvariable=num_of_page_spinebox_value,width=7).grid(row=2,column=1,ipady=1)

    # start
    start_btn = ttk.Button(top_frame,text="Start",command=on_start_btn_pressed,width=30)
    start_btn.grid(row=3,column=0,columnspan=2,**pad_option)
    global_data["start_btn"] = start_btn


    # split progress
    split_progress_bar = ttk.Progressbar(bottom_frame,mode="indeterminate",length=400)
    split_progress_bar.grid(row=0,column=0,pady=10)
    split_progress_bar.grid_forget()
    global_data["split_progress_bar"] = split_progress_bar
    


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



#########################################################################################################################



def main():
    setup_root()
    #
    setup_menu_bar()
    #
    setup_frames()
    #
    setup_widgets()
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

