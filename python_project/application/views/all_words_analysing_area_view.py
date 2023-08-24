import tkinter as tk
from tkinter import ttk

try:
    from .range_area_view import RangeArea
    from .validate_commands import ValidateCommands
except ImportError:
    from range_area_view import RangeArea
    from validate_commands import ValidateCommands


TEXT = "単語全体の分析"
RELIEF = tk.RIDGE
PAD_X = 2
PAD_Y = 0
BD = 3


class AllWordsAnalysingArea(tk.LabelFrame):
    def __init__(self, master=None, text=TEXT, padx=PAD_X, pady=PAD_Y,
                 relief=RELIEF, bd=BD, node_size=0, edge_size=0):
        super().__init__(master, text=text, padx=padx, pady=pady,
                         relief=relief, bd=bd)

        self.vcmd = ValidateCommands(int_=True)

        self.flags = dict(
            noun_pron=tk.BooleanVar(self, value=True),
            propn=tk.BooleanVar(self, value=True),
            verb=tk.BooleanVar(self, value=True),
            adj=tk.BooleanVar(self, value=True),
            adv=tk.BooleanVar(self, value=True),
            conj=tk.BooleanVar(self, value=True)
        )

        self.con_parameter_text = tk.StringVar(self)
        self.set_con_parameter(node_size=node_size, edge_size=edge_size)
        self.n_num_var = tk.IntVar(self)
        self.html_save_flag = tk.BooleanVar(self, value=False)
        self.create_widgets()

    def create_widgets(self):
        # 設定用エリア
        self.setting_area = tk.Frame(self)
        self.setting_area.pack()

        # 設定用エリア-期間設定用エリア
        self.range_area = RangeArea(self.setting_area)
        self.range_area.pack(pady=10, expand=True, fill=tk.X)

        # 設定用エリア-品詞設定用エリア
        self.hinshi_area = tk.Frame(self.setting_area)
        self.hinshi_label = tk.Label(self.hinshi_area, text="品詞を選択")
        self.checkbutton_area = tk.Frame(self.hinshi_area)
        self.noun_pron_cb = ttk.Checkbutton(
            self.checkbutton_area, text="名詞・代名詞",
            variable=self.flags["noun_pron"]
        )
        self.propn_cb = ttk.Checkbutton(
            self.checkbutton_area, text="固有名詞",
            variable=self.flags["propn"]
        )
        self.verb_cb = ttk.Checkbutton(
            self.checkbutton_area, text="動詞",
            variable=self.flags["verb"]
        )
        self.adj_cb = ttk.Checkbutton(
            self.checkbutton_area, text="形容詞",
            variable=self.flags["adj"]
        )
        self.adv_cb = ttk.Checkbutton(
            self.checkbutton_area, text="副詞",
            variable=self.flags["adv"]
        )
        self.conj_cb = ttk.Checkbutton(
            self.checkbutton_area,text="接続詞",
            variable=self.flags["conj"]
        )

        self.hinshi_area.pack(pady=10, expand=True, fill=tk.X)
        self.hinshi_label.pack(anchor=tk.W)
        self.checkbutton_area.pack()
        self.noun_pron_cb.grid(column=0, row=1, sticky=tk.W)
        self.propn_cb.grid(column=1, row=1, sticky=tk.W, padx=10)
        self.verb_cb.grid(column=2, row=1, sticky=tk.W)
        self.adj_cb.grid(column=0, row=2, sticky=tk.W)
        self.adv_cb.grid(column=1, row=2, sticky=tk.W, padx=10)
        self.conj_cb.grid(column=2, row=2, sticky=tk.W)

        # 設定用エリア-ストップワード用エリア
        self.stopword_area = tk.Frame(self.setting_area)
        self.stopword_label0 = tk.Label(
            self.stopword_area, text="ストップワードを設定"
        )
        self.stopword_area2 = tk.Frame(self.stopword_area)
        self.stopword_label1 = tk.Label(self.stopword_area2, text="上位頻出(単語数)")
        self.stopword_label2 = tk.Label(self.stopword_area2, text="下位頻出(回数)")
        self.stopword_label3 = tk.Label(self.setting_area,
                                        text="その他除外する単語(スペース区切り)")
        self.stopword_entry1 = ttk.Entry(self.stopword_area2, width=3,
                                         validate="key",
                                         validatecommand=(self.vcmd.int, "%P"))
        self.stopword_entry2 = ttk.Entry(self.stopword_area2, width=3,
                                         validate="key",
                                         validatecommand=(self.vcmd.int, "%P"))
        self.stopword_entry3 = ttk.Entry(self.setting_area)

        self.stopword_area.pack(fill=tk.X)
        self.stopword_label0.pack(anchor=tk.W)
        self.stopword_area2.pack()
        self.stopword_label1.pack(side=tk.LEFT)
        self.stopword_entry1.pack(side=tk.LEFT)
        self.stopword_label2.pack(side=tk.LEFT)
        self.stopword_entry2.pack(side=tk.LEFT)
        self.stopword_label3.pack(anchor=tk.W)
        self.stopword_entry3.pack(fill=tk.X)

        # 設定用エリア-n-gram関連エリア
        self.n_gram_area = tk.Frame(self.setting_area)
        self.n_num_label = tk.Label(self.n_gram_area,
                                    text="隣接形態素数(形態素N-gram用n数)")
        self.n_num_spinbox = ttk.Spinbox(self.n_gram_area, width=3,
                                         textvariable=self.n_num_var,
                                         from_=1, to=5, state="readonly")

        self.n_gram_area.pack(anchor=tk.E, pady=10)
        self.n_num_label.pack(side=tk.LEFT)
        self.n_num_spinbox.pack(side=tk.LEFT)

        # 設定用エリア-共起ネットワーク関連エリア
        self.min_freq_area = tk.Frame(self.setting_area)
        self.min_freq_label = tk.Label(self.min_freq_area,
                                       text="最小エッジ数(共起ネットワーク用)")
        self.min_freq_entry = ttk.Entry(self.min_freq_area, width=3,
                                        validate="key",
                                        validatecommand=(self.vcmd.int, "%P"))

        self.min_freq_area.pack(anchor=tk.E)
        self.min_freq_label.pack(side=tk.LEFT)
        self.min_freq_entry.pack(side=tk.LEFT)

        # 設定用エリア-その他ボタン類
        self.others_area = tk.Frame(self.setting_area)
        self.con_parameter_label = tk.Label(
            self.others_area,
            textvariable=self.con_parameter_text
        )
        self.df_update_button = ttk.Button(
            self.others_area, text="共起ネットワーク再計算"
        )
        self.df_button = ttk.Button(self.others_area, text="解析結果テーブルを表示")

        self.others_area.pack(expand=True, fill=tk.X, pady=10)
        self.con_parameter_label.pack()
        self.df_update_button.pack(anchor=tk.E)
        self.df_button.pack(anchor=tk.E)

        # 出力ボタン用エリア
        self.button_area = tk.Frame(self)
        self.save_cb = ttk.Checkbutton(
            self.button_area, text="htmlファイル(wordcloudは画像)を保存",
            variable=self.html_save_flag
        )
        pad = [0, 10]
        self.uni_gram_button = ttk.Button(
            self.button_area, text="uni-gramを出力", width=30, padding=pad
        )
        self.n_gram_button = ttk.Button(
            self.button_area, text="形態素N-gramを出力", width=30, padding=pad
        )
        self.wordcloud_button = ttk.Button(
            self.button_area, text="wordcloudを出力", width=30, padding=pad
        )
        self.con_button = ttk.Button(
            self.button_area, text="共起ネットワークを出力", width=30, padding=pad
        )

        self.save_cb.pack(anchor=tk.W)
        self.uni_gram_button.pack(anchor=tk.E)
        self.n_gram_button.pack(anchor=tk.E)
        self.wordcloud_button.pack(anchor=tk.E)
        self.con_button.pack(anchor=tk.E)

        self.button_area.pack(
            side=tk.BOTTOM, anchor=tk.S, expand=True, fill=tk.X, pady=10
        )

    def set_con_parameter(self, node_size, edge_size):
        main_text = f"共起ネットワークサイズ(推奨: node_size=100前後)"
        param_text = f"node_size: {node_size}, edge_size: {edge_size}"
        self.con_parameter_text.set(f"{main_text}\n{param_text}")

    def warn_incorrect_range(self):
        self.con_parameter_text.set("開始と終了が逆です。範囲を正しく選択してください。")

    def warn_failure_of_con_setting(self):
        self.con_parameter_text.set(
            "共起ネットワークの定義に失敗。\n別のパラメーターを試してください。"
        )


# テスト用
if __name__ == "__main__":
    root = tk.Tk()
    wc_cn_area = AllWordsAnalysingArea(root)
    wc_cn_area.pack(expand=True, fill=tk.Y, padx=5, pady=5)

    # test_label = tk.Label(wc_cn_area, text="ここにいろんなウィジェットを表示")
    # test_label.pack()

    # wc_cn_area.n_num_spinbox.config(state=tk.ACTIVE)
    # wc_cn_area.n_num_spinbox.insert(0, "1")
    # wc_cn_area.n_num_spinbox.config(state="readonly")

    root.mainloop()