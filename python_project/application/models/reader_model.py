from datetime import datetime
from pathlib import Path
import re
from tkinter import filedialog

import pandas as pd


def check_date(date_str):
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return False
    else:
        return True


def read_txt_file(date_str, title, file_path=None):
    # ファイルパスが渡されていない場合ダイアログを表示
    if file_path is None:
        file_path = filedialog.askopenfilename(
            title="チャットログを選択",
            filetypes=[("テキストファイル", "*.txt")]
        )
    # 読み込みファイルが存在するかどうかを確認
    if file_path and Path(file_path).exists():
        # システムメッセージを弾く正規表現パターン
        reacted_pattern = re.compile(r'Reacted to ".*" with.*')
        removed_pattern = re.compile(r'Removed a .* reaction from ".*')
        replied_pattern = re.compile(r'Replying to ".*" ')
        # ログテキストを開いて1行ずつ処理
        with open(file_path, encoding="UTF-8") as f:
            # 最初の処理でインデックスエラーを起こさないよう削除用データ入りリストを作成
            chat_list = [{
                "date": date_str,
                "title": "",
                "time": "",
                "name": "",
                "text": "",
                "reply": "",
                "delete_flag": True
            }]
            for line in f:
                # 行頭がタブではない:チャットのヘッダのため次のチャット辞書を用意
                if line[0] != "\t":
                    # 直前の辞書が削除対象となっていればそのものを削除
                    if "delete_flag" in chat_list[-1]:
                        del chat_list[-1]
                    # 行頭8文字は時刻
                    chat_time = line[0:8]
                    # DM以外は発言者名の前後が定型文のためその部分を除き発言者名を取得
                    name = line[12:-7]
                    # 新しいチャット辞書を作成
                    chat_element = {
                        "date": date_str,
                        "title": title,
                        "time": chat_time,
                        "name": name,
                        "text": "",
                        "reply": ""
                    }
                    # 行末が定型文になっていないものはDMのため削除対象に指定
                    if line[-7:] != " に 全員:\n":
                        chat_element["delete_flag"] = True
                    # 用意した新規辞書をリストに挿入
                    chat_list.append(chat_element.copy())

                # 行頭がタブである:チャット本文のためリスト末尾の辞書に本文を挿入
                else:
                    chat_list[-1]["text"] += line[1:-1] + " "

                # リプライを識別しシステムメッセージを削除
                if replied_pattern.fullmatch(chat_list[-1]["text"]):
                    chat_list[-1]["reply"] = "〇"
                    chat_list[-1]["text"] = ""

                # リアクション記録を識別し削除対象に指定
                if reacted_pattern.fullmatch(chat_list[-1]["text"]):
                    chat_list[-1]["delete_flag"] = True
                if removed_pattern.fullmatch(chat_list[-1]["text"]):
                    chat_list[-1]["delete_flag"] = True

            # for文処理後、最後に追加した辞書が削除対象となっていれば削除
            if "delete_flag" in chat_list[-1]:
                del chat_list[-1]

        # 作成した辞書リストからデータフレームを生成
        df = pd.DataFrame(chat_list)

        return df


def read_df_json_file(file_path=None):
    # ファイルパスが渡されていない場合ダイアログを表示
    if file_path is None:
        file_path = filedialog.askopenfilename(
            title="チャットログを選択",
            filetypes=[("テキストファイル", "*.txt")]
        )
    # 読み込みファイルが存在するかどうかを確認
    if file_path and Path(file_path).exists():
        df = pd.read_json(file_path, orient="records")
        df["date"] = df["date"].dt.strftime("%Y-%m-%d")
        return df
