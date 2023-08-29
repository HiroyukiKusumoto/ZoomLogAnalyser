import re
import tkinter as tk
from tkinter import ttk

import pandas as pd

try:
    from .scrollable_frame import ScrollableFrame
except ImportError:
    from scrollable_frame import ScrollableFrame


class DataFrameView(tk.Toplevel):
    """仕様データフレームを表示するポップアップ画面"""
    def __init__(self, master=None, df=None, mode=0):
        super().__init__(master)
        self.title("データフレーム")
        self.focus_set()
        self.lift()

        # treeviewを設置するスクローラブルフレーム
        self.table_frame = ScrollableFrame(self)
        self.table_frame.canvas.config(yscrollcommand="")
        # df内容を表示するtreeview
        self.table = ttk.Treeview(
            self.table_frame.main_frame,
            selectmode=tk.NONE,
            show="headings",
            height=25,
            yscrollcommand=self.table_frame.y_scrollbar.set
        )
        # スクロールバーをtreeviewに関連付け
        self.table_frame.y_scrollbar.config(command=self.table.yview)

        self.table.pack()
        self.table_frame.pack(expand=True, fill=tk.BOTH)

        # 各カラムのチェックボックスを配置するフレーム
        self.checkbutton_frame = tk.Frame(self)
        self.checkbutton_frame.pack(anchor=tk.W)
        # カラム名とチェックボックスのvariableを関連させて管理するための辞書
        self.check_flag_dict = {}

        # 現在非表示にされているアイテムを保管しておくリスト
        self.detached_items_list = []

        # その他設定の切り替えチェックボックスを配置するフレーム
        self.checkbutton_frame2 = tk.Frame(self)
        self.checkbutton_frame2.pack(anchor=tk.W)
        # self.wrap_flag = tk.BooleanVar(self, value=True)
        # self.wrap_checkbutton = ttk.Checkbutton(self.checkbutton_frame2,
        #                                         text="折り返して表示",
        #                                         variable=self.wrap_flag)
        # self.wrap_checkbutton.pack(side=tk.LEFT)
        self.all_flag = tk.BooleanVar(self, value=True)
        self.all_checkbutton = ttk.Checkbutton(self.checkbutton_frame2,
                                               text="該当要素のない項目を非表示",
                                               variable=self.all_flag,
                                               command=self.items_hide)
        self.all_checkbutton.pack(side=tk.LEFT)

        # dfがデータフレームを受け取ったときにその内容をtreeviewやチェックボックスに反映
        if type(df) == pd.DataFrame:
            # カラム名のリスト
            self.column_list = [column_name for column_name in df]
            # 第一列にindexを表示するため列を追加
            self.column_list.insert(0, "id")
            # 文字列の表示幅を確認するためのラベル(求:もっといい方法)
            width_test_label = tk.Label(self)
            # カラム(番号で管理)ごとの列幅(このあと最終的に+5pixする)を一時記録する辞書
            w_dict = {}
            # カラム名の表示幅を列幅の初期値に
            for index, name in enumerate(self.column_list):
                width_test_label.config(text=name)
                w_dict[index] = width_test_label.winfo_reqwidth()
            # treeviewにカラム名を設定
            self.table.config(columns=self.column_list)

            # dfから行ごとに要素の値を取り出してtreeviewに入れていく
            for data in df.itertuples():
                # その行の値リスト
                values_list = []
                # 要素を取り出して処理(変数は番号)
                for i in range(len(self.column_list)):
                    # 値をリストに挿入
                    values_list.append(data[i])
                    # 値を表示したときの文字列の横幅を確認(求:もっといい方法)
                    width_test_label.config(text=str(data[i]))
                    text_width = width_test_label.winfo_reqwidth()
                    # 列幅辞書の横幅と比較し大きい方を代入(最大値の記録)
                    if w_dict[i] < text_width:
                        w_dict[i] = text_width
                # 得られた行の値リストをタプル化してtreeviewに突っ込む
                values = tuple(values_list)
                self.table.insert("", tk.END, values=values,
                                  iid=str(values[0]))

            # チェックボックスのvariable辞書の初期化
            self.check_flag_dict.clear()
            # カラム名それぞれについて、チェックボックスとvariableを作成していく
            for i, column_name in enumerate(self.column_list):
                # print(f"{i}.{column_name}: {w_dict[i]}")
                # treeviewにカラム名を表示
                self.table.heading(column_name, text=column_name)
                # treeviewの列幅を列幅辞書の値+5ピクセルに設定
                self.table.column(column_name, width=w_dict[i] + 5)
                # variableを作成し、カラム名をkeyとして辞書に挿入
                flag = tk.BooleanVar(self, value=False)
                self.check_flag_dict[column_name] = flag
                # チェックボックスの作成
                checkbutton = ttk.Checkbutton(self.checkbutton_frame,
                                              text=column_name,
                                              variable=flag,
                                              command=self.columns_show)
                checkbutton.pack(side=tk.LEFT)
                # 初期表示のカラムを指定しTrueを挿入
                if mode == 0:
                    flag.set(True)
                elif mode == 1:
                    if column_name in ["words", "name", "id"]:
                        flag.set(True)

            # 選択したカラム(初期表示のもの)を表示するメソッドを実行
            self.columns_show()

    def columns_show(self):
        """variable辞書の値をすべて確認し、Trueになっているカラムを表示する"""
        # 表示するカラム名のリスト
        show_list = []
        # variable辞書からカラム名とフラグが取り出せるので、Trueのカラム名をリストに入れる
        for column_name, flag in self.check_flag_dict.items():
            if flag.get():
                show_list.append(column_name)
        # 得られたリストを表示するtreeviewのメソッドを実行
        self.table.config(displaycolumns=show_list)
        # カラム表示の更新後にアイテムの表示設定を再実行
        self.items_hide()

        self.table_frame.canvas.xview_moveto(0)
        self.after(200, self.move_window)

    def items_hide(self):
        # treeviewを初期化する(非表示アイテムを保管所から出してもとあった場所に挿入)
        for index in self.detached_items_list:
            self.table.move(index, "", int(index))
        # 非表示アイテム保管所の初期化
        self.detached_items_list.clear()
        # 空アイテムを非表示にする設定がTrueかを確認
        if self.all_flag.get():
            # treeviewから1行ずつアイテムを取り出す
            for item_id in self.table.get_children():
                # 非表示フラグ(初期値は非表示)
                hide_flag = True
                # カラム名ごとにアイテムの値を確認し空判定でない場合に非表示フラグをFalse
                for column_name in self.column_list:
                    # カラム自体が非表示の場合はスルー
                    if not self.check_flag_dict[column_name].get():
                        continue
                    # id,name,time,date,titleの5つは全てのアイテムに値があるためスルー
                    if column_name in ["id", "name", "time", "date", "title"]:
                        continue
                    # 上記に当てはまらない(値がない可能性のある表示カラム)は値の有無を確認
                    if self.table.set(item_id, column=column_name):
                        # あったばあいはFalseをフラグに入れて他のカラムを確認せず次へ
                        hide_flag = False
                        break
                # 全てのカラムでスルーされた場合、非表示アイテムを取り出し、保管所へ移動
                if hide_flag:
                    self.detached_items_list.append(item_id)
                    self.table.detach(item_id)

    def move_window(self):
        g_list = re.split(r"[x+]", self.geometry())
        if int(g_list[0]) + int(g_list[2]) > self.winfo_screenwidth():
            self.geometry(f"+0+{g_list[3]}")


if __name__ == "__main__":
    root = tk.Tk()

    def activate():
        dfv = DataFrameView(root)
        dfv.move_window()

    root.after(10, activate)

    root.mainloop()
