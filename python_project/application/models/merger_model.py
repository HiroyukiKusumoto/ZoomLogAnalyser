"""読み込み処理の段階でDataFrameをマージして被りなく処理できるようにする"""
import pandas as pd


def merge_dfs(df_list):
    """リストで与えられたデータフレームを被りなくひとつのデータフレームにまとめる"""
    merged_df = pd.DataFrame(columns=df_list[0].columns.values)
    for added_df in df_list:
        merged_df = pd.merge(merged_df, added_df, how="outer")

    return merged_df


def compare_new_and_existing_dfs(new_df, existing_df):
    """
    処理前のデータフレーム(マージ済み)を比較し、最少の解析で進められるようにする

    :param new_df: pandas.DataFrame 新たにtxtから読み込んでひとつにまとめたもの
    :param existing_df: pandas.DataFrame 処理済みでjsonから読み込んだのをまとめたもの
    :return: pandas.DataFrame nex_dfから処理する必要のない行を取り除いたデータフレーム
    """
    compared_df = pd.merge(new_df, existing_df, how="left", indicator=True)
    compared_df = compared_df[compared_df["_merge"] == "left_only"]
    compared_df = compared_df.drop("_merge", axis=1)
    compared_df = compared_df.dropna(how="all", axis=1)
    compared_df.reset_index(drop=True, inplace=True)

    return compared_df


def join_dfs(new_df, existing_df):
    """処理済みのデータフレームをまとめて日付時間順にソートし、新たなデータフレームを返す"""
    df_concat = pd.concat([existing_df, new_df], join="outer")
    df_concat = sort_df(df_concat)
    df_concat.reset_index(drop=True, inplace=True)

    return df_concat


def sort_df(df):
    """日付と時刻の行を一時的にdatetimeに変換しソートする"""
    df = df.copy()
    df["datetime"] = pd.to_datetime(df["date"] + " " + df["time"])
    df = df.sort_values("datetime")
    df.reset_index(drop=True, inplace=True)
    df = df.drop("datetime", axis=1)

    return df


def pick_range_df(df, start, end, mode=0):
    """
    rangeで与えられた範囲の行を抽出

    :param df: 抽出前のpandas.DataFrame
    :param start: 始端日付の文字列(YYYY-MM-DD)
    :param end: 終端日付の文字列(YYYY-MM-DD)
    :param mode: 処理するdfの方式
    :return: 抽出されたpandas.DataFrame
    """
    ndf = df.copy()
    start_dt = pd.to_datetime(f"{start} 00:00:00")
    end_dt = pd.to_datetime(f"{end} 23:59:59")
    if mode == 0:
        ndf["datetime"] = pd.to_datetime(ndf["date"] + " " + ndf["time"])
    elif mode == 1:
        ndf["date"] = ndf.index
        ndf["datetime"] = pd.to_datetime(ndf["date"] + " 12:00:00")
    ndf = ndf[(ndf["datetime"] >= start_dt) & (ndf["datetime"] <= end_dt)]
    ndf.reset_index(drop=True, inplace=True)
    if mode == 1:
        ndf.set_index("date", inplace=True)
    ndf = ndf.drop("datetime", axis=1)

    return ndf


def pick_names_df(df, sel_mem):
    ndf = df[df["name"].isin(sel_mem)]
    ndf.reset_index(drop=True, inplace=True)

    return ndf
