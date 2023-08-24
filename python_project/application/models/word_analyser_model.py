import re
import tkinter as tk

import pandas as pd
import spacy


PROGRESS_TEXT = "形態素解析中... "


def analyse_chats(df, i_var=None, s_var=None, kill_flag=None):
    """チャットリストからテキストを取り出し要素に分解"""
    # 言語分析の解析器を作成
    nlp = spacy.load("ja_ginza")
    docs_list = []
    all_words_list = []

    # 進捗表示
    if s_var:
        s_var.set(f"{PROGRESS_TEXT}")

    # urlの識別正規表現パターン
    url_pattern = r"https?://[\w/:%#\$&\?\(\)~\.=\+\-]+"

    counter = 0
    text_ser = df["text"]
    maximum = len(text_ser)
    # チャットひとつひとつの本文を渡していく
    for text in text_ser:
        # 中止判定
        if kill_flag and kill_flag.get():
            return None
        # 進捗表示の更新
        if i_var:
            i_var.set(counter)
        if s_var:
            s_var.set(f"{PROGRESS_TEXT}({counter}/{maximum})")
        # 抽出した単語ごとのリストを入れていくリスト(最終的に2次元リストになる)
        token_list = []
        lemma_list = []

        # 解析対象の本文からurlを取り除く処理
        text = re.sub(url_pattern, " ", text, flags=re.ASCII)

        # 本文を解析器にかけて単語に分解する処理
        doc = nlp(text)
        for sent in doc.sents:
            # 単語ひとつひとつを抽出する
            for token in sent:
                # [抽出した単語, 単語の終止形, 単語の品詞]のリストを作成し挿入
                token_list.append(
                    [token.orth_, token.lemma_, token.pos_, token.tag_]
                )
                lemma_list.append(token.lemma_)

        docs_list.append(token_list)
        all_words_list.append(lemma_list)
        counter += 1

    # 品詞分解をしたリストを要素とするSeriesを作成
    doc_ser = pd.Series(docs_list, name="doc")
    all_words_ser = pd.Series(all_words_list, name="all_words")
    # 読み込んだデータフレームの右端に結合
    df = pd.concat([df, doc_ser, all_words_ser], axis=1)

    return df
