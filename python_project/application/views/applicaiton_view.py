import tkinter as tk
from tkinterdnd2 import *

try:
    from .all_words_analysing_area_view import AllWordsAnalysingArea
    from .loading_area import LoadingAreaView
    from .member_activities_analysing_area_view import MemActsAnalysingArea
    from .selected_words_analysing_area_view import SelectedWordsAnalysingArea
    from .help_view import activate_help_window
except ImportError:
    from all_words_analysing_area_view import AllWordsAnalysingArea
    from loading_area import LoadingAreaView
    from member_activities_analysing_area_view import MemActsAnalysingArea
    from selected_words_analysing_area_view import SelectedWordsAnalysingArea
    from help_view import activate_help_window


RELIEF = tk.RIDGE
PAD_X = 4
PAD_Y = 0
BD = 3


class MainWindow(TkinterDnD.Tk):
    def __init__(self, width=None, height=None):
        super().__init__()

        self.title("Zoomログ分析")
        if isinstance(width, int) and isinstance(height, int):
            self.geometry(f"{width}x{height}")

        # メニューバーを設定
        self.menubar = tk.Menu(self)
        self.config(menu=self.menubar)

        self.set_menubar()

    def set_menubar(self):
        self.menu_file = tk.Menu(self.menubar, tearoff=False)

        self.menu_file.add_command(label="ミーティング名変更")
        self.menu_file.add_command(label="読み込み画面に戻る")
        self.menu_file.add_command(label="設定")
        self.menu_file.add_command(label="終了")

        self.menubar.add_cascade(label="ファイル", menu=self.menu_file)

        self.menu_help = tk.Menu(self.menubar, tearoff=False)

        self.menu_help.add_command(
            label="マニュアル", command=lambda: activate_help_window(self)
        )

        self.menubar.add_cascade(label="ヘルプ", menu=self.menu_help)


class ApplicationView(tk.Frame):
    def __init__(self, master, relief=RELIEF, padx=PAD_X, pady=PAD_Y, bd=BD):
        if master is None:
            master = TkinterDnD.Tk()
        super().__init__(master)
        self.pack()

        # 入力画面
        self.loading_area = LoadingAreaView(self)
        self.loading_area.pack()
        self.loading_area.loading_button.config(command=self.pushed_loading)

        # 分析に関する画面
        self.html_save_flag = tk.BooleanVar(self, value=False)
        self.s1 = AllWordsAnalysingArea(
            self, relief=relief, padx=padx, pady=pady, bd=bd
        )
        self.s1.save_cb.config(variable=self.html_save_flag)
        self.s2 = SelectedWordsAnalysingArea(
            self, relief=relief, padx=padx, pady=pady, bd=bd
        )
        self.s2.save_cb.config(variable=self.html_save_flag)
        self.s3 = MemActsAnalysingArea(
            self, relief=relief, padx=padx, pady=pady, bd=bd
        )
        self.s3.save_cb.config(variable=self.html_save_flag)

    def pushed_loading(self):
        self.loading_area.pack_forget()
        self.s1.pack(side=tk.LEFT, fill=tk.Y, anchor=tk.N, padx=5, pady=5)
        # self.s2.pack(side=tk.LEFT, fill=tk.Y, anchor=tk.N, padx=5, pady=5)
        self.s3.pack(side=tk.LEFT, fill=tk.Y, anchor=tk.N, padx=5, pady=5)


# テスト用
if __name__ == "__main__":
    main = MainWindow()
    ui = ApplicationView(main)

    ui.loading_area.loading_button.config(state=tk.ACTIVE)
    # print(ui.menu_file.entryconfig(0))
    # print(ui.menu_file.entryconfig(1))
    main.menu_file.entryconfig(1, command=lambda: print("pushed OK!"))
    main.menu_file.entryconfig(2, command=main.destroy)
    # print(ui.menu_file.entryconfig(0))

    def print_file_names(event):
        # print("action:", event.action)
        # print("actions:", event.actions)
        # print("button:", event.button)
        # print("code:", event.code)
        # print("codes:", event.codes)
        # print("commonsourcetypes:", event.commonsourcetypes)
        # print("commontargettypes:", event.commontargettypes)
        print("data:", event.data)
        # print("name:", event.name)
        # print("types:", event.types)
        # print("modifiers:", event.modifiers)
        # print("supportedsourcetypes:", event.supportedsourcetypes)
        # print("sourcetypes:", event.sourcetypes)
        # print("type:", event.type)
        # print("supportedtartettypes:", event.supportedtargettypes)
        # print("widget:", event.widget)
        # print("x_root:", event.x_root)
        # print("y_root:", event.y_root)
        # print("-" * 100)
        data_list = event.data[1:-1].split("} {")
        print(data_list)

    # ui.loading_area.dnd_label.dnd_bind("<<Drop>>", print_file_names)

    main.mainloop()
