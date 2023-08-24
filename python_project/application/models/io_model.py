"""セーブロード周りの統括的な処理"""
from datetime import datetime
from pathlib import Path

from tkinter import messagebox

try:
    from .temp_storage import DFTempStorage
    from .configures import PresetsConfig, SettingsConfig
except ImportError:
    from temp_storage import DFTempStorage
    from configures import PresetsConfig, SettingsConfig


def make_preset_dict(storage, s3_same_setting_flag):
    """現在の設定からプリセットを作成(ストレージの更新は外部で事前に呼び出すこと)"""
    new_preset = PresetsConfig.default_dict["_general_preset"].copy()

    # 共通部分
    new_preset.update(dict(
        session_name=storage.session_name
    ))

    # s1周り
    new_preset.update(dict(
        s1_range=storage.s1.range.copy(),
        s1_flags=storage.s1.flags.copy(),
        s1_stopwords=storage.s1.stopwords.copy(),
        s1_ng_words=storage.s1.ng_words.copy(),
        s1_min_edge=storage.s1.min_edge,
        s1_n_num=storage.s1.n_num
    ))

    # s3周り
    new_preset.update(dict(
        s3_range=storage.s3.range.copy(),
        s3_raw_members=storage.s3.raw_members.copy(),
        s3_custom_dict=storage.s3.custom_dict.copy(),
        s3_sel_custom=storage.s3.sel_custom.copy(),
        s3_same_setting_flag=s3_same_setting_flag
    ))

    return new_preset


def export_df(storage, settings):
    now_dt = datetime.now().strftime("%Y%m%d%H%M%S")
    session_range_st = storage.dates_list[1].replace("-", "")
    session_range_ed = storage.dates_list[-1].replace("-", "")
    session_range = f"{session_range_st}-{session_range_ed}"
    session_name = storage.session_name
    file_name = f"{now_dt}_{session_name}_{session_range}.json"

    saving_path = Path(settings.config_dict["io_config_tab"]["df_files_dir"])
    if not saving_path.exists():
        saving_path.mkdir(parents=True, exist_ok=True)
    file_path = saving_path.joinpath(file_name)

    storage.export_df(file_path)

    return file_name


def export_df_and_presets(storage, presets, settings, s3_same_f, auto=False):
    save_flag = True
    if not auto:
        save_flag = messagebox.askyesnocancel(
            "確認", "終了しようとしています。解析したデータを保存しますか？"
        )
    if save_flag is None:
        return False

    new_preset = make_preset_dict(storage, s3_same_f)
    if save_flag:
        file_name = export_df(storage, settings)
        presets.config_dict[file_name] = new_preset
    presets.config_dict[storage.session_name] = new_preset

    presets.save_config()

    return True
