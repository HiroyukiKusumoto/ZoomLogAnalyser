"""設定関連の参照先および読み書き処理"""
import json
from pathlib import Path


class BaseConfig(object):
    default_dict = {}

    def __init__(self, file_name="base.json"):
        config_dir = Path(__file__).parent.parent.parent.joinpath("0_config")
        if not config_dir.exists():
            config_dir.mkdir()
        self.config_path = config_dir.joinpath(file_name)
        self.config_dict = {}

    def _initialise(self):
        """設定ファイルが存在しなければ初期設定ファイルを作成"""
        try:
            with open(self.config_path, "x") as f:
                json.dump(self.__class__.default_dict, f, indent=4)
        except FileExistsError:
            pass

    def _check_update(self):
        """default_dictが読み込んだconfig_dictより大きければ更新"""
        default_dict = self.__class__.default_dict
        if self._check_child(self.config_dict, default_dict):
            self.config_dict = default_dict.update(self.config_dict)
            self.save_config()

    def _check_child(self, con_dict, def_dict):
        """default_dictの全ての辞書に関してkeyがconfig_dictに存在するか確認"""
        for key in def_dict:
            if key not in con_dict:
                return True
            elif isinstance(def_dict[key], dict):
                if isinstance(con_dict[key], dict):
                    if self._check_child(def_dict[key], con_dict[key]):
                        return True
        return False

    def format_configure(self):
        """設定を初期化"""
        with open(self.config_path, "w") as f:
            json.dump(self.__class__.default_dict, f, indent=4)

    def load_config(self):
        """設定を読み込み"""
        self._initialise()
        with open(self.config_path, "r") as f:
            self.config_dict = json.load(f)
        self._check_update()

    def save_config(self):
        """設定を保存"""
        try:
            with open(self.config_path, "w") as f:
                json.dump(self.config_dict, f, indent=4, ensure_ascii=False)
        except UnicodeEncodeError:
            with open(self.config_path, "w") as f:
                json.dump(self.config_dict, f, indent=4)


class SettingsConfig(BaseConfig):
    default_dict = dict(
        io_config_tab=dict(
            loading_initialdir=str(
                Path(__file__).parent.parent.parent.joinpath(
                    "1_saved_files", "df_files"
                )
            ),
            df_files_dir=str(Path(__file__).parent.parent.parent.joinpath(
                "1_saved_files", "df_files"
            )),
            figure_files_dir=str(
                Path(__file__).parent.parent.parent.joinpath(
                    "1_saved_files", "figures"
                )
            ),
            auto_loading_of_preset=True,
            select_preset_by_session_name=True,
            df_auto_save=False
        ),
        graph_config_tab=dict(
            graph_labels_editable=True,
            graph_legend_movable=False,
            scroll_zoom=False
        ),
        s1_params=dict(
            uni_gram=dict(
                title="uni-gram",
                xaxis_label="word_count",
                yaxis_label="word"
            ),
            n_gram=dict(
                title="N-gram",
                xaxis_label="word_count",
                yaxis_label="word"
            ),
            wordcloud=None,
            plt_fig_format="png",
            co_network=dict(
                title="Co-occurrence network",
                sizing=100,
                node_size="adjacency_frequency",
                color_palette="hls",
                width=1100,
                height=700
            )
        ),
        s3_params=dict(
            each=dict(
                title="number of comments",
                template="plotly_white",
                labels=dict(
                    index="date",
                    value="number of comments",
                    variable="members"
                )
            ),
            total=dict(
                title="number of comments(total)",
                template="plotly_white",
                labels=dict(
                    index="date",
                    value="number of comments(total)",
                    variable="members"
                )
            )
        )
    )

    def __init__(self):
        super().__init__("settings.json")
        self.load_config()
        self.set_dirs()

    def set_dirs(self):
        """設定された保存用ディレクトリが存在しなければ作成"""
        io_dict = self.config_dict["io_config_tab"]
        for key in io_dict:
            if isinstance(io_dict[key], str):
                if not Path(io_dict[key]).exists():
                    Path(io_dict[key]).mkdir(parents=True)


class PresetsConfig(BaseConfig):
    default_dict = dict(
        _general_preset=dict(
            session_name="",
            s1_range=dict(start="", end=""),
            s1_flags=dict(noun_pron=True,
                          propn=True,
                          verb=False,
                          adj=False,
                          adv=False,
                          conj=False),
            s1_top_n=0,
            s1_min_freq=0,
            s1_ng_words=[],
            s1_min_edge=0,
            s1_n_num=2,

            s2_range=dict(start="", end=""),
            s2_select_mode=0,
            s2_word_dict=dict(),
            s2_hinshi_dict=dict(),
            s2_output_mode=0,

            s3_range=dict(start="", end=""),
            s3_raw_members=[],
            s3_custom_dict=dict(),
            s3_sel_custom=[],
            s3_same_setting_flag=False
        )
    )

    def __init__(self):
        super().__init__("presets.json")
        self.load_config()


if __name__ == "__main__":
    bc = BaseConfig()
    sc = SettingsConfig()
    pc = PresetsConfig()
    import tkinter as tk
    root = tk.Tk()
    b1 = tk.Button(
        root, text="settingsを初期化", command=sc.format_configure
    )
    b2 = tk.Button(
        root, text="presetsを初期化", command=pc.format_configure
    )
    b1.pack(side=tk.LEFT, padx=5, pady=10)
    b2.pack(side=tk.LEFT, padx=5, pady=10)
    root.mainloop()
    print(BaseConfig.default_dict)
    print(SettingsConfig.default_dict)
    print(PresetsConfig.default_dict)
    print(bc.default_dict)
    print(sc.default_dict)
    print(pc.default_dict)
