from pathlib import Path
import re
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from tkinterdnd2 import *


class LoadingAreaView(tk.Frame):
    def __init__(self, master=None):
        if master is None:
            master = TkinterDnD.Tk()
        super().__init__(master)

        self.initialdir = None

        self.df_unit_list = []
        self.config_unit_list = []

        self.create_widgets()

    def create_widgets(self):
        self.interface_frame = tk.Frame(self)
        self.interface_frame.grid(row=0, column=0, sticky=tk.N)
        self.dnd_area = tk.Frame(self.interface_frame, width=300, height=200)
        self.dnd_area.propagate(False)
        self.dnd_area.pack(padx=5)

        self.dnd_label = ttk.Label(
            self.dnd_area,
            relief="groove",
            anchor=tk.CENTER,
            text="ここにファイルまたはフォルダをドラッグ&ドロップして読み込み"
        )
        self.dnd_label.pack(pady=5, fill=tk.BOTH, expand=True)
        self.dnd_label.drop_target_register(DND_FILES)
        self.dnd_label.dnd_bind("<<Drop>>", self.check_dropped_files)
        self.browse_button = ttk.Button(
            self.dnd_area, text="参照", command=self.browse_and_select_file
        )
        self.browse_button.pack(side=tk.BOTTOM, anchor=tk.E)

        self.radiobutton_area = tk.Frame(self.interface_frame)
        # self.radiobutton_area.pack(padx=5, pady=10, anchor=tk.W)
        self.rb_var = tk.IntVar(value=0)
        self.date_only_rb = ttk.Radiobutton(
            self.radiobutton_area,
            variable=self.rb_var,
            value=0,
            text="日付でミーティングを区別"
        )
        self.num_only_rb = ttk.Radiobutton(
            self.radiobutton_area,
            variable=self.rb_var,
            value=1,
            text="回数でミーティングを区別"
        )
        self.both_rb = ttk.Radiobutton(
            self.radiobutton_area,
            variable=self.rb_var,
            value=2,
            text="日付・回数でミーティングを区別"
        )
        self.date_only_rb.grid(row=0, column=0, sticky=tk.W)
        self.num_only_rb.grid(row=1, column=0, sticky=tk.W)
        self.both_rb.grid(row=2, column=0, sticky=tk.W)

        self.loading_button = ttk.Button(
            self.interface_frame,
            text="読込実行",
            padding=[20,5],
            state=tk.DISABLED
        )
        self.loading_button.pack(side=tk.BOTTOM, pady=5)

        self.list_frame = tk.Frame(self)
        self.list_frame.grid(row=0, column=1, sticky=tk.N)
        self.df_list_area = tk.Frame(self.list_frame)
        self.df_list_area.pack(anchor=tk.W)

    def browse_and_select_file(self):
        f_type = [
            ("対応ファイル", ".txt .json"),
            ("ログファイル", ".txt"),
            ("解析済ログ", ".json")
        ]
        file = filedialog.askopenfilename(
            title="読み込みファイル選択",
            filetypes=f_type,
            initialdir=self.initialdir
        )
        if file:
            path = Path(file)
            self.check_selected_file(path)

        self.loading_button_setting()

    def check_dropped_files(self, event):
        event_data_tuple = self.tk.splitlist(event.data)

        for data in event_data_tuple:
            path = Path(data).resolve()
            if path.is_dir():
                path = path.joinpath("meeting_saved_chat.txt")
            if path.exists():
                self.check_selected_file(path)

        self.loading_button_setting()

    def check_selected_file(self, path):
        file_name = path.name

        if file_name.endswith(".txt"):
            self.set_config_unit(path)
        if file_name.endswith(".json"):
            self.set_dataframe_unit(path)

    def set_config_unit(self, path):
        dir_name = path.parent.name
        index = len(self.config_unit_list)
        config_unit = LoadingFilesConfigUnit(self.list_frame, index)
        self.config_unit_list.append(config_unit)

        if len(dir_name) >= 20:
            if re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", dir_name[:10]):
                config_unit.date_entry.insert(0, dir_name[:10])
                config_unit.session_name_entry.insert(0, dir_name[20:])
        config_unit.file_path_label.config(text=str(path))

        if self.rb_var.get() == 0:
            config_unit.num_entry.grid_forget()
        elif self.rb_var.get() == 1:
            config_unit.date_entry.grid_forget()
        config_unit.destroy_button.config(
            command=lambda: self.remove_config_unit(index)
        )

        config_unit.pack(anchor=tk.W, fill=tk.X)

    def remove_config_unit(self, index):
        config_unit = self.config_unit_list[index]
        config_unit.destroy()
        self.config_unit_list[index] = None
        self.loading_button_setting()

    def set_dataframe_unit(self, path):
        index = len(self.df_unit_list)
        df_unit = LoadingDataframeUnit(self.df_list_area, index)
        self.df_unit_list.append(df_unit)

        df_unit.file_path_label.config(text=str(path))

        df_unit.destroy_button.config(
            command=lambda: self.remove_df_unit(index)
        )

        df_unit.pack(fill=tk.X, expand=True)

    def remove_df_unit(self, index):
        df_unit = self.df_unit_list[index]
        df_unit.destroy()
        self.df_unit_list[index] = None
        self.loading_button_setting()

    def loading_button_setting(self):
        for item in self.config_unit_list:
            if item:
                self.loading_button.config(state=tk.ACTIVE)
                return
        for item in self.df_unit_list:
            if item:
                self.loading_button.config(state=tk.ACTIVE)
                return
        self.loading_button.config(state=tk.DISABLED)


class LoadingFilesConfigUnit(tk.Frame):
    def __init__(self, master=None, index=None):
        super().__init__(master)
        self.index = index

        self.date_entry = ttk.Entry(self, width=10)
        self.num_entry = ttk.Entry(self, width=6)
        self.session_name_entry = ttk.Entry(self)
        self.file_path_label = tk.Label(self, anchor=tk.E,
                                        width=75, relief="groove")
        self.destroy_button = tk.Button(self, text="×")

        self.date_entry.grid(row=0, column=0)
        self.num_entry.grid(row=0, column=1)
        self.session_name_entry.grid(row=0, column=2)
        self.file_path_label.grid(row=0, column=3)
        self.destroy_button.grid(row=0, column=4)


class LoadingDataframeUnit(tk.Frame):
    def __init__(self, master=None, index=None):
        super().__init__(master)
        self.index = index

        self.file_path_label = tk.Label(self, anchor=tk.E, width=100)
        self.destroy_button = tk.Button(self, text="×")

        self.file_path_label.pack(side=tk.LEFT, anchor=tk.E)
        self.destroy_button.pack(side=tk.RIGHT)
