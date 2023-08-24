# ※要編集(230501)　フラグの扱い
# 編集済(230508)　要検証
import tkinter as tk

import pandas as pd


def select_words(df, filter_words=None, flags=None):
    # データフレームから解析結果の列を抜き出す
    doc_ser = df["doc"]

    # 既にwordsが抽出されていた場合初期化
    if "words" in df.columns:
        df = df.drop("words", axis=1)

    # 品詞ごとに抽出したリストを投入
    words_lists_list = []
    for doc in doc_ser:
        words_list = []
        for token in doc:
            # 選択器にかける
            word = choice_word(token, filter_words, flags)
            if word is not None:
                words_list.append(word)
        words_lists_list.append(words_list)

    words_ser = pd.Series(words_lists_list, name="words")
    df = pd.concat([df, words_ser], axis=1)

    return df


def choice_word(token, filter_words=None, flags=None, flag_number=None):
    """品詞フラグとNGワードを確認し解析する単語に含めるか採択"""
    lemma_ = token[1]
    pos_ = token[2]
    tag_ = token[3]
    # NGワードがあれば合致していないかを確認
    if filter_words is not None:
        if lemma_ in filter_words:
            return None

    # flagsが設定されていない場合にフィルターするリストを設定
    if flags is None:
        flags = dict(
            noun_pron=True,
            propn=True,
            verb=True,
            adj=True,
            adv=True,
            conj=True
        )
    # flag_numberが指定された場合にフィルターするリストを設定
    if flag_number is None:
        flag_nums = [True for _ in range(6)]
    elif flag_number in [i for i in range(6)]:
        flag_nums = [False for _ in range(6)]
        flag_nums[flag_number] = True
    else:
        flag_nums = [False for _ in range(6)]

    # 各品詞について、表示設定があって単語が該当するならその単語そのものを返す
    if flags["noun_pron"] and flag_nums[0]:
        if pos_ == "NOUN" and tag_ != "空白" or pos_ == "PRON":
            return lemma_

    if flags["propn"] and flag_nums[1]:
        if pos_ == "PROPN":
            return lemma_

    if flags["verb"] and flag_nums[2]:
        if pos_ == "VERB":
            return lemma_

    if flags["adj"] and flag_nums[3]:
        if pos_ == "ADJ":
            return lemma_

    if flags["adv"] and flag_nums[4]:
        if pos_ == "ADV":
            return lemma_

    if flags["conj"] and flag_nums[5]:
        if pos_ == "CONJ" or pos_ == "SCONJ":
            return lemma_

    # 何もなければNone
    return None
