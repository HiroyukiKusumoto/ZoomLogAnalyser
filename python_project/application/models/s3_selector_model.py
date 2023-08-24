import pandas as pd

try:
    from .temp_storage import S3DFTempStorage
except ImportError:
    from temp_storage import S3DFTempStorage


def selection_info_update(s3_st, new_cus_dict=None, new_sel_cus=None):
    # custom_dictが変更された(詳細画面の更新後など)ときにstorageとcustom_membersを更新
    if new_cus_dict is not None:
        s3_st.custom_dict = new_cus_dict
        cus_mem_list = s3_st.raw_members.copy()
        for key, val_list in s3_st.custom_dict.items():
            if key in cus_mem_list:
                cus_mem_list.remove(key)
            for val in val_list:
                if val in cus_mem_list:
                    cus_mem_list.remove(val)
        for key in s3_st.custom_dict:
            cus_mem_list.append(key)
        s3_st.custom_members = cus_mem_list

    # sel_customが変更されているときにstorageを更新
    if new_sel_cus is not None:
        s3_st.sel_custom = new_sel_cus

    # 新しいcustom_membersに存在しないsel_customの要素を削除
    s3_st.sel_custom = list(set(s3_st.sel_custom) & set(s3_st.custom_members))

    # sel_rawを更新
    sel_raw_list = []
    for mem in s3_st.sel_custom:
        if mem in s3_st.custom_dict:
            for inner_name in s3_st.custom_dict[mem]:
                if inner_name not in sel_raw_list:
                    sel_raw_list.append(inner_name)
        else:
            sel_raw_list.append(mem)
    s3_st.sel_raw = sel_raw_list


def initial_resolve_df(df):
    item_list = []
    dates_np_list = df["date"].unique()
    dates_list = dates_np_list.tolist()
    for dt in dates_list:
        one_day_df = df[df["date"] == dt]
        count_ser = one_day_df["name"].value_counts()
        count_ser.rename(dt, inplace=True)
        item_list.append(count_ser)

    new_df = pd.DataFrame(item_list).fillna(0)

    return new_df


def make_custom_df(df, sel_custom, custom_dict):
    ser_dict = {}
    for name in sel_custom:
        if name in custom_dict:
            unit_df = df.filter(items=custom_dict[name], axis=1)
            ser_dict[name] = unit_df.sum(axis=1)
        else:
            ser_dict[name] = df[name]
    new_df = pd.DataFrame(ser_dict)

    return new_df


def make_total_df(df):
    return df.cumsum(axis=0)
