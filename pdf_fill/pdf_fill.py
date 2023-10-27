import tkinter as tk 
import tkinter.ttk as ttk
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter.simpledialog import askinteger

from utils import load_data, load_coordinate, fill, disable_children_widgets, enable_children_widgets

import os
import threading

import gettext






class MainWindow:
    def __init__(self):
        self.setup_root()
        #
        self.setup_menu_bar()
        #
        self.setup_frames()
        #
        self.setup_widgets()

        #
        self.center_window(self.root)

        #init
        self.on_multiple_files_chk_pressed()
        self.output_file_count = 1 # used for suffix
        self.template_file_path = ""
        self.data_file_path = ""
        self.coord_file_path = ""
        self.output_file_path = ""
        
    

    #######################################################################################################################
    # logic

    


    #######################################################################################################################
    # event handler

    def on_about_btn_pressed(self):
        about_window = tk.Toplevel(self.root)
        about_window.title("About")
        about_window.geometry("400x250")
        about_window.resizable(0,0)
        about_window.rowconfigure(0,weight=1)
        about_window.columnconfigure(0,weight=1)
        self.center_window(about_window)
        #
        about_window_frm = ttk.Frame(about_window)
        about_window_frm.grid()
        #
        txt = "Tkinter\nReportLab\nPyPDF2\nopenpyxl\narabic-reshaper\npython-bidi\n______\nver 0.1\nhttps://github.com/sapy22"

        about_text = tk.Text(about_window_frm,height=10,width=40)
        about_text.grid(row=0,column=0)
        about_text.tag_configure('tag-center', justify='center')
        about_text.insert("1.0",txt,"tag-center")
        about_text.configure(state="disable")

        ttk.Button(about_window_frm, text="Exit",command=about_window.destroy).grid(row=1,column=0,pady=10)
        #
        about_window.grab_set()
    

    def on_template_file_btn_pressed(self):
        template_file_path = askopenfilename(filetypes=[("PDF Files", "*.pdf")])

        if template_file_path and not template_file_path.endswith(".pdf"):
            tk.messagebox.showerror(_("Error"),_("Please select PDF files only"))
            template_file_path = ""
            
        # init
        if not template_file_path:
            self.template_file_lbl_value.set(_("Please select the template file (pdf)"))
            self.template_file_path = ""
            return

        if len(template_file_path) > 40:
            t_template_file_path = template_file_path[:15]+"/ ... /"+template_file_path[-25:]
        else:
            t_template_file_path = template_file_path
        
        self.template_file_lbl_value.set(t_template_file_path)

        self.template_file_path = template_file_path

        self.template_file_page_num = self._get_page_num()

    def _get_page_num(self):
        page_num = askinteger(_("Select Page Number"),_("Enter the page number to fill: "))

        if page_num != None:
            if page_num <= 0:
                page_num = 0
            elif page_num > 0:
                page_num = page_num - 1
        else:
            page_num = 0
        
        return page_num


    def on_data_file_btn_pressed(self):
        data_file_path = askopenfilename(filetypes=[("Excel Files", "*.xlsx")])

        if data_file_path and not data_file_path.endswith(".xlsx"):
            tk.messagebox.showerror(_("Error"),_("Please select excel Files only"))
            data_file_path = ""
            
        # init
        if not data_file_path:
            self.data_file_lbl_value.set(_("Please select the data file (excel)"))
            self.data_file_path = ""
            return

        if len(data_file_path) > 40:
            t_data_file_path = data_file_path[:15]+"/ ... /"+data_file_path[-25:]
        else:
            t_data_file_path = data_file_path
        
        self.data_file_lbl_value.set(t_data_file_path)

        self.data_file_path = data_file_path


    def on_coord_file_btn_pressed(self):
        coord_file_path = askopenfilename(filetypes=[("Text Files", "*.txt")])

        if coord_file_path and not coord_file_path.endswith(".txt"):
            tk.messagebox.showerror(_("Error"),_("Please select text files only"))
            coord_file_path = ""
            
        # init
        if not coord_file_path:
            self.coord_file_lbl_value.set(_("Please select the coordinates file (txt)"))
            self.coord_file_path = ""
            return

        if len(coord_file_path) > 40:
            t_coord_file_path = coord_file_path[:15]+"/ ... /"+coord_file_path[-25:]
        else:
            t_coord_file_path = coord_file_path
        
        self.coord_file_lbl_value.set(t_coord_file_path)

        self.coord_file_path = coord_file_path
    

    def on_output_file_btn_pressed(self):
        output_file_path = asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf")],
        )
            
        # init
        if not output_file_path:
            self.output_file_lbl_value.set(_("Please select the output file (pdf)"))
            self.output_file_path = ""
            return

        if len(output_file_path) > 40:
            t_output_file_path = output_file_path[:15]+"/ ... /"+output_file_path[-25:]
        else:
            t_output_file_path = output_file_path
        
        self.output_file_lbl_value.set(t_output_file_path)

        self.output_file_path = output_file_path


    def on_multiple_files_chk_pressed(self):
        if self.multiple_files_chk_value.get() == 1:
            tk.messagebox.showwarning(_("Warning"),_("1- Suffix can't contain invalid characters \\ / : * ? \" < > |\nso it will be replaced with -\n2- Suffix need to be unique or the files will be overwritten"))
            enable_children_widgets(self.suffix_lbl_frm)
        
        elif self.multiple_files_chk_value.get() == 0:
            disable_children_widgets(self.suffix_lbl_frm)
                


    def on_start_btn_pressed(self):
        if self.template_file_path and self.data_file_path and self.coord_file_path and self.output_file_path:
            #
            def _is_valid():
                coord = load_coordinate(self.coord_file_path)
                _data = load_data(self.data_file_path)
                row = next(_data)
                if len(row) == len(coord):
                    output_file_name = self._get_output_file_name(row)
                    if output_file_name:
                        self.output_file_count = 1 # re init after validating
                        return True
                    else:
                        tk.messagebox.showerror(_("Error"),_("File name is invalid"))
                        return False
                else:
                    tk.messagebox.showerror(_("Error"),_("The length of data file columns doesn't match the length of the coordinates"))
                    return False
            
            #
            self.fill_err_msg = ""
            def _start():
                coord = load_coordinate(self.coord_file_path)
                data = load_data(self.data_file_path)
                font_setting = [self.font_name_cmbo_value.get(),int(self.font_size_cmbo_value.get()),self.font_color_cmbo_value.get(),self.font_alignment_cmbo_value.get()]

                for row in data:
                    output_file_name = self._get_output_file_name(row)

                    r = fill(row, coord,font_setting,self.template_file_path,self.template_file_page_num,output_file_name)
                    
                    if r != None:
                        self.fill_err_msg = r
                        break
            

            
            if _is_valid():
                self.start_btn.configure(state="disable")
                disable_children_widgets(self.multiple_files_frm)

                t = threading.Thread(target=_start)
                t.start()

                self._update_fill_progress(t)
        
        else:
            tk.messagebox.showerror(_("Error"),_("Please select the template\data\coordinates\output files"))

    
    def _get_output_file_name(self,row):
        try:
            if self.multiple_files_chk_value.get() == 1:
                file_name_full = os.path.basename(self.output_file_path)
                dir_name = os.path.dirname(self.output_file_path)

                file_name = file_name_full.split(".")[0]

                # suffix
                if self.suffix_rdo_value.get() == 0:
                    suffix = self._get_data_col_suffix(row)
                elif self.suffix_rdo_value.get() == 1:
                    suffix = self.output_file_count
                    self.output_file_count += 1

                output_file_name = os.path.join(dir_name,f"{file_name}_{suffix}.pdf")

            else:
                output_file_name = self.output_file_path

            return output_file_name

        except:
            return None


    def _get_data_col_suffix(self,row):
        col_num = self.data_col_spn_value.get()
        try:
            col_num = int(col_num)
            if col_num <= 0:
                col_num = 0
            elif col_num > 0:
                col_num = col_num - 1

            suffix = str(row[col_num])

            for l in suffix:
                if l in ["\\","/",":","*","?","\"","<",">","|"]:
                    suffix = suffix.replace(l,"-")
            #
            return suffix
        #
        except ValueError:
            tk.messagebox.showerror(_("Error"),_("Wrong column number!!"))
            raise
        except IndexError:
            tk.messagebox.showerror(_("Error"),_("Wrong column number!!"))
            raise
        except Exception as e:
            print(e)
            raise
    

    def _update_fill_progress(self,thread):

        if thread.is_alive():
            self.root.after(500,lambda: self._update_fill_progress(thread))
        else:
            if self.fill_err_msg:
                tk.messagebox.showerror(_("Error"),self.fill_err_msg)

            else:
                tk.messagebox.showinfo(_("Info"),_("Done"))

            self.start_btn.configure(state="normal")
            
            if self.multiple_files_chk_value.get() == 1:
                enable_children_widgets(self.multiple_files_frm)
            else:
                self.multiple_files_chk_btn.configure(state="normal")
            



    #######################################################################################################################
    # gui

    def setup_root(self):
        self.root = tk.Tk()
        self.root.title("pdf_fill")
        self.root.geometry("480x380")
        self.root.resizable(0,0)
        self.root.rowconfigure(0,weight=1)
        self.root.columnconfigure(0,weight=1)


    def setup_menu_bar(self):
        menu_bar = tk.Menu()

        help_menu = tk.Menu(menu_bar, tearoff=0)

        help_menu.add_command(label="About", command=self.on_about_btn_pressed)

        menu_bar.add_cascade(label="Help", menu=help_menu)

        self.root.config(menu=menu_bar)


    def setup_frames(self):
        main_frame = ttk.Frame(self.root)
        main_frame.grid(row=0,column=0)

        top_frame = ttk.Frame(main_frame)
        top_frame.grid(row=0,column=0)

        self.bootom_frame = ttk.Frame(main_frame)
        self.bootom_frame.grid(row=1,column=0)

        #
        notebook = ttk.Notebook(top_frame)
        notebook.grid()

        self.notebook_main = ttk.Frame(notebook)
        self.notebook_main.grid(row=0,column=0)

        notebook.add(self.notebook_main,text=_("Main"))

        
        self.notebook_setting = ttk.Frame(notebook)
        self.notebook_setting.grid(row=0,column=0)

        notebook.add(self.notebook_setting,text=_("Setting"))



    

    def setup_widgets(self):
        pad_option = {"padx":5,"pady":5,"ipadx":5,"ipady":5}

        # template
        self.template_file_lbl_value = tk.StringVar(value=_("Please select the template file (pdf)"))
        ttk.Label(self.notebook_main,textvariable=self.template_file_lbl_value,width=40,background="white").grid(row=0,column=0,**pad_option)

        ttk.Button(self.notebook_main,text=_("Template File"),command=self.on_template_file_btn_pressed,width=15).grid(row=0,column=1,**pad_option)

        # data
        self.data_file_lbl_value = tk.StringVar(value=_("Please select the data file (excel)"))
        ttk.Label(self.notebook_main,textvariable=self.data_file_lbl_value,width=40,background="white").grid(row=1,column=0,**pad_option)

        ttk.Button(self.notebook_main,text=_("Data File"),command=self.on_data_file_btn_pressed,width=15).grid(row=1,column=1,**pad_option)

        # coord
        self.coord_file_lbl_value = tk.StringVar(value=_("Please select the coordinates file (txt)"))
        ttk.Label(self.notebook_main,textvariable=self.coord_file_lbl_value,width=40,background="white").grid(row=2,column=0,**pad_option)

        ttk.Button(self.notebook_main,text=_("Coordinates File"),command=self.on_coord_file_btn_pressed,width=15).grid(row=2,column=1,**pad_option)
        
        # output
        self.output_file_lbl_value = tk.StringVar(value=_("Please select the output file (pdf)"))
        ttk.Label(self.notebook_main,textvariable=self.output_file_lbl_value,width=40,background="white").grid(row=3,column=0,**pad_option)

        ttk.Button(self.notebook_main,text=_("Output File"),command=self.on_output_file_btn_pressed,width=15).grid(row=3,column=1,**pad_option)

        # multiple files
        self.multiple_files_frm = ttk.Frame(self.notebook_main)
        self.multiple_files_frm.grid(row=4,column=0,columnspan=2,pady=20)
        
        self.multiple_files_chk_value = tk.IntVar(value=0)
        self.multiple_files_chk_btn = ttk.Checkbutton(self.multiple_files_frm,text=_("Multiple Files"),variable=self.multiple_files_chk_value,command=self.on_multiple_files_chk_pressed)
        self.multiple_files_chk_btn.grid(row=0,column=0,**pad_option)

        self.suffix_lbl_frm = ttk.Labelframe(self.multiple_files_frm,text=_("Suffix"))
        self.suffix_lbl_frm.grid(row=0,column=1)

        self.suffix_rdo_value = tk.IntVar(value=0)
        ttk.Radiobutton(self.suffix_lbl_frm,text=_("Data column"),variable=self.suffix_rdo_value,value=0).grid(row=0,column=0)

        self.data_col_spn_value = tk.StringVar(value="1")
        ttk.Spinbox(self.suffix_lbl_frm,from_=1,to=999,textvariable=self.data_col_spn_value,width=5).grid(row=0,column=1,padx=10)

        ttk.Radiobutton(self.suffix_lbl_frm,text=_("Increment"),variable=self.suffix_rdo_value,value=1).grid(row=0,column=2,padx=20)


        # font
        font_lbl_frm = ttk.Labelframe(self.notebook_setting,text=_("Font"))
        font_lbl_frm.grid(row=6,column=0,**pad_option)

        ttk.Label(font_lbl_frm,text=_("Name :")).grid(row=0,column=0,sticky="w")
        self.font_name_cmbo_value = tk.StringVar(value="ARIAL")
        ttk.Combobox(font_lbl_frm,textvariable=self.font_name_cmbo_value,values=["ARIAL","Helvetica","Courier"],state="readonly").grid(row=0,column=1,padx=10)

        ttk.Label(font_lbl_frm,text=_("Size :")).grid(row=1,column=0,sticky="w",pady=10)
        self.font_size_cmbo_value = tk.StringVar(value="12")
        ttk.Combobox(font_lbl_frm,textvariable=self.font_size_cmbo_value,values=["8","10","12","14","16","18","20"],state="readonly").grid(row=1,column=1)

        ttk.Label(font_lbl_frm,text=_("Color :")).grid(row=2,column=0,sticky="w")
        self.font_color_cmbo_value = tk.StringVar(value="Black")
        ttk.Combobox(font_lbl_frm,textvariable=self.font_color_cmbo_value,values=["Black","Red","Blue","Green"],state="readonly").grid(row=2,column=1)

        ttk.Label(font_lbl_frm,text=_("Text Alignment :")).grid(row=3,column=0,sticky="w",pady=10)
        self.font_alignment_cmbo_value = tk.StringVar(value="Left")
        ttk.Combobox(font_lbl_frm,textvariable=self.font_alignment_cmbo_value,values=["Left","Right"],state="readonly").grid(row=3,column=1)


        # start
        self.start_btn = ttk.Button(self.bootom_frame,text="Start",command=self.on_start_btn_pressed,width=30)
        self.start_btn.grid(row=1,column=0,columnspan=2,padx=10,pady=20,ipadx=10,ipady=10)


    def center_window(self,window):
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


#######################################################################################################################################







if __name__ == "__main__":

    lang = "EN"

    if lang == "AR":
        ar = gettext.translation('pdf_coordinate', localedir='locale', languages=['ar'])
        ar.install()
        _ = ar.gettext
    else:
        _ = gettext.gettext

    
    app = MainWindow()
    app.root.mainloop()