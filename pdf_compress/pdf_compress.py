import os
import subprocess
import tkinter as tk
import tkinter.ttk as ttk
from concurrent.futures import ThreadPoolExecutor
import threading
import time
from tkinter.filedialog import askdirectory, askopenfilenames
from tkinter import messagebox

import gettext




"""
this is a multi thread app

thread > thread pool > subprocess

- spwaning a thread so that the main thread keep updating the gui 
- using thread pool for multiple subprocess
- using subprocess because i am calling an external program 

"""


# dpi 300 > ~150  > 75
# printer > ebook > screen

########################################################################################################################################################

debug_print = False

compression_setting = {0:"ebook",1:"screen"}

global_data = {
   "root":None,
   "top_frame":None,
   "bottom_frame":None,
   "compression_lvl_frame":None,
   "input_files_lbl_value":None,
   "output_folder_lbl_value":None,
   "compression_lvl_radio_btn_value":None,
   "start_btn":None,
   "compress_progress_bar":None,
   "compress_progress_lbl_value":None,
   "input_files_path":"",
   "output_folder_path":"",
   "compressed_files_count" : 0,
   "input_files_count":0,
   "output_file_postfix":"compressed"
}


#######################################################################################################################################################
# logic

def compress():
   start_time = time.time()

   arg = _get_file_names()
   with ThreadPoolExecutor() as executor:
      executor.map(_compress, arg)
   
   if debug_print:
      print(f"completed in {time.time() - start_time} seconds")


def _get_file_names():
   input_files = global_data["input_files_path"]
   output_folder = global_data["output_folder_path"]

   arg_tuple_list = []
   for input_file_path in input_files:
      in_file_name = os.path.basename(input_file_path)
      output_file_name = in_file_name.split(".")[0]
      postfix = global_data["output_file_postfix"]

      output_file_path = os.path.join(output_folder,f"{output_file_name}_{postfix}.pdf")
      #
      arg_tuple_list.append((input_file_path,output_file_path))

   return arg_tuple_list


def _compress(arg: tuple):
   input_file_name, output_file_name = arg
   compression_lvl = compression_setting[global_data["compression_lvl_radio_btn_value"].get()]

   
   args = ['gswin64c', '-sDEVICE=pdfwrite', '-dCompatibilityLevel=1.5', f'-dPDFSETTINGS=/{compression_lvl}', '-dNOPAUSE', '-dBATCH',  '-dQUIET', 
                     f"-sOutputFile={output_file_name}", input_file_name]

   sui = subprocess.STARTUPINFO()
   sui.dwFlags |= subprocess.STARTF_USESHOWWINDOW

   j = subprocess.Popen(args,startupinfo=sui,stdout=subprocess.PIPE).wait()
   
   global_data["compressed_files_count"] += 1

   if debug_print:
      print(global_data["compressed_files_count"])


#####################################################################################################################################
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
   Ghostscript
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


def on_input_files_btn_pressed():
   input_files = askopenfilenames(filetypes=[("PDF Files", "*.pdf")])

   for f in input_files:
      if not f.endswith(".pdf"):
         messagebox.showerror(_("Error"),_("Please select PDF files only"))
         input_files = ()
         break

   if not input_files:
      _init_input()
      return
   
   if len(input_files[0]) > 40:
      t_input_files = input_files[0][:15]+"/ ... /"+input_files[0][-25:]

   else:
      t_input_files = input_files

   global_data["input_files_lbl_value"].set(t_input_files)

   global_data["input_files_path"] = input_files

   global_data["input_files_count"] = len(input_files)
   
def _init_input():
   global_data["input_files_path"] = ""
   global_data["input_files_lbl_value"].set(_("Please select the input files"))


def on_output_folder_btn_pressed():
   output_folder = askdirectory()

   if not output_folder:
      _init_output()
      return

   if len(output_folder) > 40:
      t_output_folder = output_folder[:15]+"/ ... /"+output_folder[-25:]

   else:
      t_output_folder = output_folder

   global_data["output_folder_lbl_value"].set(t_output_folder)

   global_data["output_folder_path"] = output_folder

def _init_output():
   global_data["output_folder_path"] = ""
   global_data["output_folder_lbl_value"].set(_("Please select the output folder"))


def on_start_btn_pressed():
   if global_data["input_files_path"] and global_data["output_folder_path"]:
      _init_progress()

      t = threading.Thread(target=compress)
      t.start()
      
      _update_compress_progress(t)
   else:
      messagebox.showerror(_("Error"),_("Please select The input and output folder"))

def _init_progress():
   global_data["start_btn"]["state"] = "disabled"
   global_data["compress_progress_bar"]["maximum"] = global_data["input_files_count"]
   global_data["compressed_files_count"] = 0


def _update_compress_progress(thread):
   input_files_count = global_data["input_files_count"]
   compressed_files_count = global_data["compressed_files_count"]

   global_data["compress_progress_bar"]["value"] = float(compressed_files_count)
   global_data["compress_progress_lbl_value"].set(f"{compressed_files_count} of {input_files_count}")

   if thread.is_alive():
      global_data["root"].after(100,lambda: _update_compress_progress(thread))
   else:
      messagebox.showinfo(_("Info"),_("Done"))

      global_data["start_btn"]["state"] = "normal"



###########################################################################################################################
# gui

def setup_root():
   root = tk.Tk()
   root.title("pdf_compress")
   root.geometry("500x400")
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

   compression_lvl_frame = ttk.LabelFrame(top_frame,text=_("Compression Level"))
   compression_lvl_frame.grid(row=2,column=0,columnspan=2,pady=10,sticky="we")
   global_data["compression_lvl_frame"] = compression_lvl_frame
   

def setup_widgets():
   top_frame = global_data["top_frame"]
   compression_lvl_frame = global_data["compression_lvl_frame"] 
   bottom_frame = global_data["bottom_frame"]
   
   pad_option = {"padx":10,"pady":10,"ipadx":10,"ipady":10}

   # input
   input_files_lbl_value = tk.StringVar(value=_("Please select the input files"))
   ttk.Label(top_frame,textvariable=input_files_lbl_value,width=40).grid(row=0,column=0,**pad_option)
   global_data["input_files_lbl_value"] = input_files_lbl_value

   ttk.Button(top_frame,text=_("Input Files"),command=on_input_files_btn_pressed).grid(row=0,column=1,**pad_option)

   # output
   output_folder_lbl_value = tk.StringVar(value=_("Please select the output folder"))
   ttk.Label(top_frame,textvariable=output_folder_lbl_value,width=40).grid(row=1,column=0,**pad_option)
   global_data["output_folder_lbl_value"] = output_folder_lbl_value

   ttk.Button(top_frame,text=_("Output Folder"),command=on_output_folder_btn_pressed).grid(row=1,column=1,**pad_option)

   # compression level
   compression_lvl_radio_btn_value = tk.IntVar(value=0)
   ttk.Radiobutton(compression_lvl_frame,text=_("Normal (recommended)"),variable=compression_lvl_radio_btn_value,value=0).grid(row=2,column=0,**pad_option)
   ttk.Radiobutton(compression_lvl_frame,text=_("High (low quality Image)"),variable=compression_lvl_radio_btn_value,value=1).grid(row=2,column=1,**pad_option)
   global_data["compression_lvl_radio_btn_value"] = compression_lvl_radio_btn_value

   # start
   start_btn = ttk.Button(top_frame,text="Start",command=on_start_btn_pressed,width=30)
   start_btn.grid(row=3,column=0,columnspan=2,**pad_option)
   global_data["start_btn"] = start_btn

   # compress progress
   compress_progress_bar = ttk.Progressbar(bottom_frame,value=0,maximum=100,mode="determinate",length=400)
   compress_progress_bar.grid(row=0,column=0,pady=10)
   global_data["compress_progress_bar"] = compress_progress_bar
   
   compress_progress_lbl_value = tk.StringVar(value="")
   ttk.Label(bottom_frame,textvariable=compress_progress_lbl_value).grid(row=1,column=0,pady=10)
   global_data["compress_progress_lbl_value"] = compress_progress_lbl_value


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


   

###############################################################################################################################


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




if __name__ == "__main__":

   lang = "EN"

   if lang == "AR":
      ar = gettext.translation('pdf_coordinate', localedir='locale', languages=['ar'])
      ar.install()
      _ = ar.gettext
   else:
      _ = gettext.gettext


   main()