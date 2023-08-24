from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

try:
    from .validate_commands import ValidateCommands
except ImportError:
    from validate_commands import ValidateCommands


def pack_widgets(widgets_dict, **kwargs):
    """辞書内(多重可)に存在するウィジェットをすべて同じオプションでpackする"""
    for key in widgets_dict:
        if isinstance(widgets_dict[key], dict):
            pack_widgets(widgets_dict[key], **kwargs)
        else:
            widgets_dict[key].pack(**kwargs)


def reset_values(widgets_dict):
    """辞書内(多重可)に存在するユニットたちをすべてresetする"""
    for key in widgets_dict:
        if isinstance(widgets_dict[key], dict):
            reset_values(widgets_dict[key])
        else:
            widgets_dict[key].reset()


class ConfigToplevel(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)

        self.title("設定")
        self.lift()
        self.focus_set()

        self.widgets = {}

        self.create_widgets()

    def create_widgets(self):
        # 下部ボタン領域の設定
        button_area = tk.Frame(self)
        self.widgets["button_area"] = dict(
            ok_button=ttk.Button(button_area, text="OK"),
            cancel_button=ttk.Button(button_area, text="キャンセル"),
            apply_button=ttk.Button(button_area, text="適用")
        )
        pack_widgets(self.widgets["button_area"], side=tk.LEFT)
        button_area.pack(side=tk.BOTTOM, anchor=tk.E, padx=5)

        # メイン設定領域のタブ準備
        main_notebook = ttk.Notebook(self)
        io_config_tab = tk.Frame(main_notebook, padx=2, pady=5)
        graph_config_tab = tk.Frame(main_notebook, padx=2, pady=5)
        s1_params_tab = tk.Frame(main_notebook, padx=2, pady=5)
        s3_params_tab = tk.Frame(main_notebook, padx=2, pady=5)
        gen_pre_config_tab = tk.Frame(main_notebook, padx=2, pady=5)
        main_notebook.add(io_config_tab, text="読込/保存")
        main_notebook.add(graph_config_tab, text="グラフ全般")
        main_notebook.add(s1_params_tab, text="単語全体の分析")
        main_notebook.add(s3_params_tab, text="参加者の発言数分析")
        main_notebook.add(gen_pre_config_tab, text="初期処理")
        main_notebook.pack(anchor=tk.W, padx=5, pady=5)

        # I/O周りの設定項目
        self.widgets["io_config_tab"] = dict(
            loading_initialdir=DirectorySelectUnit(
                io_config_tab, text="読み込みログファイル選択ダイアログの初期表示フォルダ"
            ),
            df_files_dir=DirectorySelectUnit(
                io_config_tab, "終了時のデータフレーム自動保存先フォルダ"
            ),
            figure_files_dir=DirectorySelectUnit(
                io_config_tab, "グラフ・画像の保存先フォルダ"
            ),
            auto_loading_of_preset=CheckbuttonUnit(
                io_config_tab,
                "処理済みデータフレーム読み込み時、前回の処理設定を自動で引き継ぐ"
            ),
            select_preset_by_session_name=CheckbuttonUnit(
                io_config_tab,
                "未処理ログ読み込み時、前回の処理設定をミーティング名から判断して引き継ぐ"
            ),
            df_auto_save=CheckbuttonUnit(
                io_config_tab, "終了時に解析データを自動保存する"
            )
        )
        pack_widgets(self.widgets["io_config_tab"], fill=tk.X)
        space = tk.Frame(io_config_tab)
        space.pack(pady=15)

        # グラフ化周りの共通設定項目
        self.widgets["graph_config_tab"] = dict(
            graph_labels_editable=CheckbuttonUnit(
                graph_config_tab,
                text="グラフタイトル・ラベルをブラウザ上で編集する"
            ),
            graph_legend_movable=CheckbuttonUnit(
                graph_config_tab, text="凡例を移動可能にする"
            ),
            scroll_zoom=CheckbuttonUnit(
                graph_config_tab, text="マウスホイールでグラフを拡大・縮小する"
            )
        )
        pack_widgets(self.widgets["graph_config_tab"], fill=tk.X)
        space = tk.Frame(graph_config_tab)
        space.pack(pady=15)

        # 形態素分析のグラフ設定項目
        self.widgets["s1_params"] = dict(
            plt_fig_format=ListSelectUnit(
                s1_params_tab,
                text="ワードクラウドを画像保存するときのファイル形式",
                choices_list=["emf", "eps", "jpg", "pdf", "png", "ps",
                              "raw", "rgba", "svg", "svgz", "tif"]
            ),
            uni_gram=dict(
                title=InputUnit(s1_params_tab, "uni-gramのグラフタイトル"),
                xaxis_label=InputUnit(s1_params_tab, "uni-gramのX軸ラベル"),
                yaxis_label=InputUnit(s1_params_tab, "uni-gramのY軸ラベル")
            ),
            n_gram=dict(
                title=InputUnit(s1_params_tab, "形態素N-gramのグラフタイトル"),
                xaxis_label=InputUnit(s1_params_tab, "形態素N-gramのX軸ラベル"),
                yaxis_label=InputUnit(s1_params_tab, "形態素N-gramのY軸ラベル")
            ),
            co_network=dict(
                title=InputUnit(s1_params_tab, "共起ネットワークのタイトル")
            )
        )
        pack_widgets(self.widgets["s1_params"], fill=tk.X)
        space = tk.Frame(s1_params_tab)
        space.pack(pady=15)

        # 発言数分析のグラフ設定項目
        self.widgets["s3_params"] = dict(
            each=dict(
                title=InputUnit(s3_params_tab, "発言数推移のグラフタイトル"),
                labels=dict(
                    index=InputUnit(s3_params_tab, "発言数推移のX軸ラベル"),
                    value=InputUnit(s3_params_tab, "発言数推移のY軸ラベル"),
                    variable=InputUnit(s3_params_tab, "発言数推移の凡例タイトル")
                ),
                template=ListSelectUnit(
                    s3_params_tab,
                    "発言数推移のグラフテーマ",
                    choices_list=[
                        "ggplot2", "seaborn", "simple_white", "plotly",
                        "plotly_white", "plotly_dark", "presentation",
                        "xgridoff", "ygridoff", "gridon", "none"
                    ]
                )
            ),
            total=dict(
                title=InputUnit(s3_params_tab, "発言数推移(累計)のグラフタイトル"),
                labels=dict(
                    index=InputUnit(s3_params_tab, "発言数推移(累計)のX軸ラベル"),
                    value=InputUnit(s3_params_tab, "発言数推移(累計)のY軸ラベル"),
                    variable=InputUnit(s3_params_tab, "発言数推移(累計)の凡例タイトル")
                ),
                template=ListSelectUnit(
                    s3_params_tab,
                    "発言数推移(累計)のグラフテーマ",
                    choices_list=[
                        "ggplot2", "seaborn", "simple_white", "plotly",
                        "plotly_white", "plotly_dark", "presentation",
                        "xgridoff", "ygridoff", "gridon", "none"
                    ]
                )
            )
        )
        pack_widgets(self.widgets["s3_params"], fill=tk.X)
        space = tk.Frame(s3_params_tab)
        space.pack(pady=15)

        # 初期処理周りの設定項目
        self.widgets["gen_pre_config_tab"] = dict(
            s1_flags=HinshiCheckbuttonArea(gen_pre_config_tab),
            s1_top_n=InputIntUnit(gen_pre_config_tab, "ストップワード:上位頻出(単語数)"),
            s1_min_freq=InputIntUnit(gen_pre_config_tab, "ストップワード:下位頻出(回数)"),
            s1_ng_words=InputListUnit(
                gen_pre_config_tab, "その他除外する単語(スペース区切り)"
            ),
            s1_min_edge=InputIntUnit(gen_pre_config_tab, "最小エッジ数(共起ネットワーク用)")
        )
        pack_widgets(self.widgets["gen_pre_config_tab"], fill=tk.X)
        space = tk.Frame(gen_pre_config_tab)
        space.pack(pady=15)

        # リセットボタン集
        self.widgets["reset_buttons"] = dict(
            io_config_tab=ttk.Button(io_config_tab, text="このタブを初期化"),
            graph_config_tab=ttk.Button(graph_config_tab, text="このタブを初期化"),
            s1_params=ttk.Button(s1_params_tab, text="このタブを初期化"),
            s3_params=ttk.Button(s3_params_tab, text="このタブを初期化"),
            gen_pre_config_tab=ttk.Button(gen_pre_config_tab, text="このタブを初期化")
        )
        pack_widgets(
            self.widgets["reset_buttons"], side=tk.BOTTOM, anchor=tk.E
        )

        # リセット挙動を設定
        for tab_name in self.widgets["reset_buttons"]:
            self.widgets["reset_buttons"][tab_name].config(
                command=lambda: reset_values(self.widgets[tab_name])
            )


class DirectorySelectUnit(tk.Frame):
    def __init__(self, master, text="項目名未指定"):
        super().__init__(master, pady=2)
        self.default = ""
        vcmd = ValidateCommands(filepath=True)
        varidate_dict = dict(
            validate="key", validatecommand=(vcmd.filepath, "%P")
        )

        self.label = tk.Label(self, text=text)
        frame = tk.Frame(self)
        self.entry = ttk.Entry(frame, width=50, **varidate_dict)
        self.browse_button = ttk.Button(frame, text="参照", command=self.browse)

        self.label.pack(anchor=tk.W)
        frame.pack(anchor=tk.E)
        self.entry.grid(row=0, column=0)
        self.browse_button.grid(row=0, column=1)

    def browse(self):
        new_path = filedialog.askdirectory(parent=self)
        if new_path:
            self.set(new_path)

    def set(self, value):
        self.entry.delete(0, tk.END)
        self.entry.insert(0, value)
        self.entry.xview_moveto(1)

    def get(self):
        new_path = self.entry.get()
        if not Path(new_path).exists():
            messagebox.showwarning(
                title="警告",
                message=f"「{self.label.cget('text')}」に入力された\n"
                        f"'{new_path}'は\n存在しないため、この項目は更新されませんでした。"
            )
            return None
        if new_path:
            return new_path
        return None

    def set_default(self, value):
        self.default = value

    def reset(self):
        self.set(self.default)


class InputUnit(tk.Frame):
    def __init__(self, master, text="項目名未指定"):
        super().__init__(master, pady=2)
        self.default = ""
        self.label = tk.Label(self, text=text)
        self.entry = ttk.Entry(self, width=55)

        self.label.pack(anchor=tk.W)
        self.entry.pack(anchor=tk.E)

    def set(self, value):
        self.entry.delete(0, tk.END)
        if isinstance(value, str):
            self.entry.insert(0, value)
        else:
            self.entry.insert(0, str(value))

    def get(self):
        new_str = self.entry.get()
        if new_str:
            return new_str
        return None

    def set_default(self, value):
        self.default = value

    def reset(self):
        self.set(self.default)


class InputIntUnit(InputUnit):
    def __init__(self, master, text="項目名未指定"):
        super().__init__(master, text)
        self.label.pack_forget()
        self.entry.pack_forget()

        vcmd = ValidateCommands(int_=True)
        self.entry.config(
            width=5,
            justify=tk.RIGHT,
            validate="key",
            validatecommand=(vcmd.int, "%P")
        )
        self.label.pack(side=tk.LEFT)
        self.entry.pack(side=tk.RIGHT)


class InputListUnit(InputUnit):
    def __init__(self, master, text="項目名未指定"):
        super().__init__(master, text)
        self.default = []

    def set(self, values_list):
        super().set(" ".join(values_list))

    def get(self):
        return self.entry.get().split()


class ListSelectUnit(tk.Frame):
    def __init__(self, master, text="項目名未指定", choices_list=None):
        super().__init__(master, pady=2)
        self.default = ""
        if choices_list is None:
            choices_list = []
        self.label = tk.Label(self, text=text)
        self.cbox = ttk.Combobox(self, values=choices_list, state="readonly")

        self.label.pack(anchor=tk.W)
        self.cbox.pack(anchor=tk.E)

    def set(self, value):
        self.cbox.set(value)

    def get(self):
        return self.cbox.get()

    def set_default(self, value):
        self.default = value

    def reset(self):
        self.set(self.default)


class CheckbuttonUnit(tk.Frame):
    def __init__(self, master, text="項目名未指定"):
        super().__init__(master, pady=2)
        self.default = True
        self.var = tk.BooleanVar(self)
        self.cbutton = ttk.Checkbutton(self, text=text, variable=self.var)
        self.cbutton.pack(side=tk.LEFT)

    def set(self, value):
        self.var.set(value)

    def get(self):
        return self.var.get()

    def set_default(self, value):
        self.default = value

    def reset(self):
        self.set(self.default)


class HinshiCheckbuttonArea(tk.Frame):
    def __init__(self, master, text="品詞の選択"):
        super().__init__(master, pady=2)
        self.default = {}
        self.label = tk.Label(self, text=text)
        checkbutton_area = tk.Frame(self)
        cbs_dict = dict(
            noun_pron=ttk.Checkbutton(checkbutton_area, text="名詞・代名詞"),
            propn=ttk.Checkbutton(checkbutton_area, text="固有名詞"),
            verb=ttk.Checkbutton(checkbutton_area, text="動詞"),
            adj=ttk.Checkbutton(checkbutton_area, text="形容詞"),
            adv=ttk.Checkbutton(checkbutton_area, text="副詞"),
            conj=ttk.Checkbutton(checkbutton_area, text="接続詞")
        )
        self.variables = {}
        for key in cbs_dict:
            self.variables[key] = tk.BooleanVar(self)
            cbs_dict[key].config(variable=self.variables[key])
        cbs_dict["noun_pron"].grid(row=0, column=0, sticky=tk.W)
        cbs_dict["propn"].grid(row=0, column=1, sticky=tk.W, padx=10)
        cbs_dict["verb"].grid(row=0, column=2, sticky=tk.W)
        cbs_dict["adj"].grid(row=1, column=0, sticky=tk.W)
        cbs_dict["adv"].grid(row=1, column=1, sticky=tk.W, padx=10)
        cbs_dict["conj"].grid(row=1, column=2, sticky=tk.W)
        self.label.pack(anchor=tk.W)
        checkbutton_area.pack()

    def set(self, values_dict):
        for key in values_dict:
            self.variables[key].set(values_dict[key])

    def get(self):
        return {key: self.variables[key].get() for key in self.variables}

    def set_default(self, values_dict):
        self.default = values_dict.copy()

    def reset(self):
        self.set(self.default)


if __name__ == "__main__":
    root = tk.Tk()

    def activate_window():
        cf = ConfigToplevel(root)
        # cf.widgets["button_area"]["ok_button"].config(command=lambda: print(
        #     cf.widgets["io_config_tab"]["figure_files_dir"].get()
        # ))
        # cf.widgets["button_area"]["cancel_button"].config(
        #     command=lambda: print(
        #         cf.widgets["io_config_tab"]["auto_loading_of_preset"].get()
        #     )
        # )
        # cf.widgets["button_area"]["apply_button"].config(
        #     command=lambda: print(
        #         cf.widgets["gen_pre_config_tab"]["s1_ng_words"].get()
        #     )
        # )

    button = tk.Button(root, text="展開", command=activate_window)
    button.pack(padx=20, pady=10)

    root.mainloop()
