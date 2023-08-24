import tkinter as tk
from tkinter import ttk

try:
    from .range_area_view import RangeArea
except ImportError:
    from range_area_view import RangeArea


TEXT = "抜き出し分析"
RELIEF = tk.RIDGE
PAD_X = 2
PAD_Y = 0
BD = 3


class SelectedWordsAnalysingArea(tk.LabelFrame):
    def __init__(self, master=None, text=TEXT, padx=PAD_X, pady=PAD_Y,
                 relief=RELIEF, bd=BD):
        super().__init__(master, text=text, padx=padx, pady=pady,
                         relief=relief, bd=bd)

        self.rb_var1 = tk.IntVar(self, value=0)
        self.rb_var2 = tk.IntVar(self, value=0)

        self.hinshi_list = []

        self.wsu_list = []
        self.hsu_list = []

        self.html_save_flag = tk.BooleanVar(self, value=False)
        self.create_widgets()

    def create_widgets(self):
        # 設定用エリア
        self.setting_area = tk.Frame(self)
        self.setting_area.pack()

        # 設定用エリア-期間設定用エリア
        self.range_area = RangeArea(self.setting_area)
        self.range_area.pack(pady=10, expand=True, fill=tk.X)

        # 設定用エリア-単語抽出用エリア
        self.each_word_rb = tk.Radiobutton(
            self.setting_area, text="単語を抜き出し",
            variable=self.rb_var1, value=0, command=self.check_change
        )
        self.each_word_area = ttk.LabelFrame(
            self.setting_area, labelwidget=self.each_word_rb
        )
        self.word_select_label = tk.Label(
            self.each_word_area, text="単語を指定して抽出"
        )

        self.word_select_label.pack(anchor=tk.W)
        wsu = WordSelectUnit(self.each_word_area)
        wsu.add_button.bind(
            sequence="<ButtonPress>", func=self._pushed_add_wsu
        )
        wsu.destroy_button.bind(
            sequence="<ButtonPress>", func=self.destroy_wsu
        )
        wsu.first_unit()
        self.wsu_list.append(wsu)
        wsu.pack(expand=True, fill=tk.X)
        self.each_word_area.pack(expand=True, fill=tk.X)

        # 設定用エリア-品詞抽出用エリア
        self.each_hinshi_rb = tk.Radiobutton(
            self.setting_area, text="品詞を抜き出し",
            variable=self.rb_var1, value=1, command=self.check_change
        )
        self.each_hinshi_area = ttk.LabelFrame(
            self.setting_area, labelwidget=self.each_hinshi_rb
        )
        self.hinshi_select_label = tk.Label(
            self.each_hinshi_area, text="品詞を指定して抽出"
        )

        self.hinshi_select_label.pack(anchor=tk.W)
        hsu = HinshiSelectUnit(self.each_hinshi_area)
        hsu.combobox.config(values=self.hinshi_list)
        hsu.add_button.bind(
            sequence="<ButtonPress>", func=self._pushed_add_hsu
        )
        hsu.destroy_button.bind(
            sequence="<ButtonPress>", func=self.destroy_hsu
        )
        hsu.first_unit()
        self.hsu_list.append(hsu)
        hsu.pack(expand=True, fill=tk.X)
        self.each_hinshi_area.pack(expand=True, fill=tk.X)

        # 設定用エリア-その他ボタン類
        # self.df_update_button = ttk.Button(self.setting_area,
        #                                    text="データフレームを更新")
        self.df_button = ttk.Button(self.setting_area, text="解析結果テーブルを表示")

        # self.df_update_button.pack(anchor=tk.E)
        self.df_button.pack(anchor=tk.E)

        self.check_change()

        # 出力ボタン用エリア
        self.button_area = tk.Frame(self)
        self.all_day_rb = ttk.Radiobutton(
            self.button_area, text="日付によらず合計値で集計",
            variable=self.rb_var2, value=0
        )
        self.each_day_rb = ttk.Radiobutton(
            self.button_area, text="日付ごとに集計",
            variable=self.rb_var2, value=1
        )
        self.save_cb = ttk.Checkbutton(
            self.button_area, text="htmlファイルを保存",
            variable=self.html_save_flag
        )
        pad = [0, 10]
        self.uni_gram_button = ttk.Button(
            self.button_area, text="棒グラフを出力", width=30, padding=pad
        )

        self.all_day_rb.pack(anchor=tk.W)
        self.each_day_rb.pack(anchor=tk.W)
        self.save_cb.pack(anchor=tk.W)
        self.uni_gram_button.pack(anchor=tk.E)

        self.button_area.pack(
            side=tk.BOTTOM, anchor=tk.S, expand=True, fill=tk.X, pady=10
        )

    def check_change(self):
        if self.rb_var1.get() == 0:
            for wsu in self.wsu_list:
                wsu.enable_unit()
            for hsu in self.hsu_list:
                hsu.disable_unit()
            self.wsu_list[0].first_unit()
        elif self.rb_var1.get() == 1:
            for wsu in self.wsu_list:
                wsu.disable_unit()
            for hsu in self.hsu_list:
                hsu.enable_unit()
            self.hsu_list[0].first_unit()

    def _pushed_add_wsu(self, event=None):
        if event is not None:
            if event.widget["state"] != tk.DISABLED:
                unit = self.nametowidget(event.widget.winfo_parent())
                id_ = self.wsu_list.index(unit)
                self.add_wsu(id_)

    def add_wsu(self, id_):
        new_wsu = WordSelectUnit(self.each_word_area)
        new_wsu.add_button.bind(
            sequence="<ButtonPress>", func=self._pushed_add_wsu
        )
        new_wsu.destroy_button.bind(
            sequence="<ButtonPress>", func=self.destroy_wsu
        )
        id_ += 1
        self.wsu_list.insert(id_, new_wsu)
        while id_ < len(self.wsu_list):
            self.wsu_list[id_].pack_forget()
            self.wsu_list[id_].pack(expand=True, fill=tk.X)
            id_ += 1

    def destroy_wsu(self, event=None):
        if event is not None:
            if event.widget["state"] != tk.DISABLED:
                unit = self.nametowidget(event.widget.winfo_parent())
                id = self.wsu_list.index(unit)
                del self.wsu_list[id]
                unit.destroy()
                self.wsu_list[0].first_unit()

    def _pushed_add_hsu(self, event=None):
        if event is not None:
            if event.widget["state"] != tk.DISABLED:
                unit = self.nametowidget(event.widget.winfo_parent())
                id_ = self.hsu_list.index(unit)
                self.add_hsu(id_)

    def add_hsu(self, id_):
        new_hsu = HinshiSelectUnit(self.each_hinshi_area)
        new_hsu.add_button.bind(
            sequence="<ButtonPress>", func=self._pushed_add_hsu
        )
        new_hsu.destroy_button.bind(
            sequence="<ButtonPress>", func=self.destroy_hsu
        )
        id_ += 1
        self.hsu_list.insert(id_, new_hsu)
        while id_ < len(self.hsu_list):
            self.hsu_list[id_].pack_forget()
            self.hsu_list[id_].pack(expand=True, fill=tk.X)
            id_ += 1

    def destroy_hsu(self, event=None):
        if event is not None:
            if event.widget["state"] != tk.DISABLED:
                unit = self.nametowidget(event.widget.winfo_parent())
                id = self.hsu_list.index(unit)
                del self.hsu_list[id]
                unit.destroy()
                self.hsu_list[0].first_unit()


class WordSelectUnit(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)

        self.entry = ttk.Entry(self)
        self.cb_var = tk.BooleanVar(self, value=False)
        self.combine_cb = ttk.Checkbutton(
            self, text="上の項目に統合", variable=self.cb_var
        )
        self.add_button = tk.Button(self, text="+")
        self.destroy_button = tk.Button(self, text="×")

        self.entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.combine_cb.pack(side=tk.LEFT)
        self.add_button.pack(side=tk.LEFT)
        self.destroy_button.pack(side=tk.LEFT)

    def first_unit(self):
        self.combine_cb.config(state=tk.DISABLED)
        self.destroy_button.config(state=tk.DISABLED)

    def enable_unit(self):
        self.entry.config(state=tk.ACTIVE)
        self.combine_cb.config(state=tk.ACTIVE)
        self.add_button.config(state=tk.ACTIVE)
        self.destroy_button.config(state=tk.ACTIVE)

    def disable_unit(self):
        self.entry.config(state=tk.DISABLED)
        self.combine_cb.config(state=tk.DISABLED)
        self.add_button.config(state=tk.DISABLED)
        self.destroy_button.config(state=tk.DISABLED)

    def get_value(self):
        return self.entry.get()

    def get_var(self):
        return self.cb_var.get()


class HinshiSelectUnit(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)

        self.combobox = ttk.Combobox(self, state="readonly")
        self.cb_var = tk.BooleanVar(self, value=False)
        self.combine_cb = ttk.Checkbutton(
            self, text="上の項目に統合", variable=self.cb_var
        )
        self.add_button = tk.Button(self, text="+")
        self.destroy_button = tk.Button(self, text="×")

        self.combobox.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.combine_cb.pack(side=tk.LEFT)
        self.add_button.pack(side=tk.LEFT)
        self.destroy_button.pack(side=tk.LEFT)

    def first_unit(self):
        self.combine_cb.config(state=tk.DISABLED)
        self.destroy_button.config(state=tk.DISABLED)

    def enable_unit(self):
        self.combobox.config(state="readonly")
        self.combine_cb.config(state=tk.ACTIVE)
        self.add_button.config(state=tk.ACTIVE)
        self.destroy_button.config(state=tk.ACTIVE)

    def disable_unit(self):
        self.combobox.config(state=tk.DISABLED)
        self.combine_cb.config(state=tk.DISABLED)
        self.add_button.config(state=tk.DISABLED)
        self.destroy_button.config(state=tk.DISABLED)

    def get_value(self):
        return self.combobox.get()

    def get_var(self):
        return self.cb_var.get()


# テスト用
if __name__ == "__main__":
    root = tk.Tk()
    wc_cn_area = SelectedWordsAnalysingArea(root)
    wc_cn_area.pack(expand=True, fill=tk.Y, padx=5, pady=5)

    # test_label = tk.Label(wc_cn_area, text="ここにいろんなウィジェットを表示")
    # test_label.pack()

    # l = wc_cn_area.wsu_list
    # print(l[0])
    # print(l[0].add_button.winfo_parent())
    # print(l.index(wc_cn_area.nametowidget(l[0].add_button.winfo_parent())))

    root.mainloop()