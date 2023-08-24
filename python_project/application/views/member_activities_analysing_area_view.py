import tkinter as tk
from tkinter import ttk

try:
    from .member_activities_selection_view import MemActsDetailSelectionToplevel
    from .range_area_view import RangeArea
except ImportError:
    from member_activities_selection_view import MemActsDetailSelectionToplevel
    from range_area_view import RangeArea


TEXT = "参加者の発言数分析"
RELIEF = tk.RIDGE
PAD_X = 2
PAD_Y = 0
BD = 3


class MemActsAnalysingArea(tk.LabelFrame):
    def __init__(self, master=None, text=TEXT, padx=PAD_X, pady=PAD_Y,
                 relief=RELIEF, bd=BD, name_list=None):
        super().__init__(master, text=text, padx=padx, pady=pady,
                         relief=relief, bd=bd)

        if name_list is None:
            self.name_list = [f"test{i}" for i in range(30)]
        else:
            self.name_list = name_list

        self.list_var = tk.StringVar(self)
        self.list_var.set(self.name_list)
        self.same_setting_flag = tk.BooleanVar(self, value=False)
        self.html_save_flag = tk.BooleanVar(self, value=False)
        self.create_widgets()

    def create_widgets(self):
        # 設定用エリア
        self.setting_area = tk.Frame(self)
        self.setting_area.pack()

        # 設定用エリア-期間設定用エリア
        self.range_area = RangeArea(self.setting_area)
        self.range_area.pack(pady=10, expand=True, fill=tk.X)

        # 設定用エリア-表示選択エリア
        self.member_select_area = tk.Frame(self.setting_area)
        self.member_select_area.pack(expand=True, fill=tk.X)

        self.member_select_label = tk.Label(
            self.member_select_area, text="集計する対象を選択"
        )
        self.listbox = tk.Listbox(
            self.member_select_area, height=10, width=40,
            listvariable=self.list_var, selectmode=tk.MULTIPLE,
            exportselection=False
        )
        self.scrollbar = ttk.Scrollbar(
            self.member_select_area,
            orient=tk.VERTICAL,
            command=self.listbox.yview
        )
        self.listbox.config(yscrollcommand=self.scrollbar.set)
        self.select_button_area = tk.Frame(self.member_select_area)
        self.all_select_button = ttk.Button(
            self.select_button_area, text="全て選択",
            command=lambda: self.listbox.select_set(0, tk.END)
        )
        self.all_clear_button = ttk.Button(
            self.select_button_area, text="全て解除",
            command=lambda: self.listbox.select_clear(0, tk.END)
        )
        self.advanced_setting_button = ttk.Button(
            self.select_button_area, text="詳細", command=self.open_detail
        )
        self.same_setting_checkbutton = ttk.Checkbutton(
            self.member_select_area,
            text="他の分析にもこの設定を使用",
            variable=self.same_setting_flag
        )

        self.member_select_label.grid(row=0, column=0, sticky=tk.W)
        self.listbox.grid(row=1, column=0)
        self.scrollbar.grid(row=1, column=1, sticky=tk.NS)
        self.select_button_area.grid(
            row=2, column=0, columnspan=2, sticky=tk.E
        )
        self.all_select_button.pack(side=tk.LEFT)
        self.all_clear_button.pack(side=tk.LEFT)
        self.advanced_setting_button.pack(side=tk.LEFT)
        self.same_setting_checkbutton.grid(
            row=3, column=0, columnspan=2, sticky=tk.E
        )

        # 設定用エリア-その他ボタン類
        self.df_button_area = tk.Frame(self.setting_area)
        self.df_button1 = ttk.Button(
            self.df_button_area, text="解析結果テーブルを表示(日毎)"
        )
        self.df_button2 = ttk.Button(
            self.df_button_area, text="解析結果テーブルを表示(累計)"
        )

        self.df_button_area.pack(fill=tk.X, pady=10)
        self.df_button1.pack(anchor=tk.E)
        self.df_button2.pack(anchor=tk.E)

        # 出力ボタン用エリア
        self.button_area = tk.Frame(self)
        self.save_cb = ttk.Checkbutton(
            self.button_area, text="htmlファイルを保存",
            variable=self.html_save_flag
        )
        pad = [0, 10]
        self.each_day_graph_button = ttk.Button(
            self.button_area, text="発言数推移を出力", width=30, padding=pad
        )
        self.all_day_graph_button = ttk.Button(
            self.button_area, text="合計発言数推移を出力", width=30, padding=pad
        )

        self.save_cb.pack(anchor=tk.W)
        self.each_day_graph_button.pack(anchor=tk.E)
        self.all_day_graph_button.pack(anchor=tk.E)

        self.button_area.pack(
            side=tk.BOTTOM, anchor=tk.S, expand=True, fill=tk.X, pady=10
        )

    def open_detail(self, custom_dict=None):
        detail_window = MemActsDetailSelectionToplevel(
            self, name_list=self.name_list.copy(), custom_dict=custom_dict
        )


if __name__ == "__main__":
    root = tk.Tk()
    activities_area = MemActsAnalysingArea(root)
    activities_area.pack(expand=True, fill=tk.Y, padx=5, pady=5)

    print(type(activities_area.list_var.get()))

    root.mainloop()
