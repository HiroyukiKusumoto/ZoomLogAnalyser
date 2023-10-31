from pathlib import Path
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

import pandas as pd

try:
    from ..models import *
    from ..views.applicaiton_view import ApplicationView
    from ..views.applicaiton_view import MainWindow
    from ..views.config_view import ConfigToplevel
    from ..views.data_frame_view import DataFrameView
    from ..views.member_activities_selection_view \
        import MemActsDetailSelectionToplevel
    from ..views.progress_dialog_view import ProgressDialog
    from ..views.session_name_input_view import SessionNameInputView
except ImportError:
    import sys
    sys.path.append("../../")
    from application.models import *
    from application.views.applicaiton_view import ApplicationView
    from application.views.applicaiton_view import MainWindow
    from application.views.config_view import ConfigToplevel
    from application.views.data_frame_view import DataFrameView
    from application.views.member_activities_selection_view \
        import MemActsDetailSelectionToplevel
    from application.views.progress_dialog_view import ProgressDialog
    from application.views.session_name_input_view import SessionNameInputView


class MainController(object):
    def __init__(self, root):
        self.root = root
        self.settings = configures.SettingsConfig()
        self.presets = configures.PresetsConfig()
        self.storage = temp_storage.DFTempStorage()

        self.ui = ApplicationView(root)

        self.root.menu_file.entryconfig(0, state=tk.DISABLED)
        self.root.menu_file.entryconfig(1, state=tk.DISABLED)
        self.root.menu_file.entryconfig(2, command=self.config_open)
        self.root.menu_file.entryconfig(3, command=self.root.destroy)

        # 読み込んだsettingsの内容を各所に反映
        plotter_model.PlotterModel.save_path = Path(
            self.settings.config_dict["io_config_tab"]["figure_files_dir"]
        )
        self.storage.dir_path = Path(
            self.settings.config_dict["io_config_tab"]["df_files_dir"]
        )
        self.ui.loading_area.initialdir = self.settings.config_dict[
            "io_config_tab"
        ]["loading_initialdir"]
        self.ui.loading_area.loading_button.config(
            command=self.reading_execution_at_main
        )

    @staticmethod
    def is_df(df):
        """データフレームであり、かつ空でない"""
        return isinstance(df, pd.DataFrame) and not df.empty

    def change_session_name(self):
        """session_nameの変更メニューを呼び出す"""
        sni = SessionNameInputView(self.root, self.storage.session_name)
        self.root.wait_window(sni)
        if sni.result is not None:
            self.storage.session_name = sni.result

    def config_open(self):
        """設定画面を開く(「設定」が押されたときの処理)"""
        cw = ConfigToplevel(self.ui)

        # 各ユニットに現設定を適用
        self.config_view_set(cw)
        self.config_view_set_default(cw)

        # 下部3つのボタンの挙動設定
        cw.widgets["button_area"]["ok_button"].config(
            command=lambda: self.config_ok(cw)
        )
        cw.widgets["button_area"]["cancel_button"].config(
            command=lambda: self.config_close(cw)
        )
        cw.widgets["button_area"]["apply_button"].config(
            command=lambda: self.update_config(cw)
        )

        # ×ボタンの挙動設定
        cw.protocol("WM_DELETE_WINDOW", lambda: self.config_close(cw))

        # 2重の設定画面を防止
        self.root.menu_file.entryconfig(2, command=cw.lift)

    def config_ok(self, config_window):
        """設定画面でOKが押された時の処理"""
        self.update_config(config_window)
        self.config_close(config_window)

    def config_close(self, config_window):
        """設定画面でキャンセルあるいは×ボタンが押されたときの処理"""
        config_window.destroy()
        self.root.menu_file.entryconfig(2, command=self.config_open)

    def config_view_set(self, config_window):
        """設定画面を開いたあと現在の設定値を表示する"""
        MainController.settings_set(
            config_window.widgets, self.settings.config_dict
        )
        MainController.preset_set(
            config_window.widgets["gen_pre_config_tab"],
            self.presets.config_dict["_general_preset"]
        )

    @staticmethod
    def settings_set(widgets_dict, settings_default_dict):
        """設定画面用現在値設定(settings編)"""
        for key in widgets_dict:
            if key in settings_default_dict:
                if isinstance(widgets_dict[key], dict):
                    MainController.settings_set(
                        widgets_dict[key], settings_default_dict[key]
                    )
                else:
                    widgets_dict[key].set(settings_default_dict[key])

    @staticmethod
    def preset_set(widgets_dict, preset_default_dict):
        """設定画面用現在値設定(preset編)"""
        for key in widgets_dict:
            widgets_dict[key].set(preset_default_dict[key])

    def update_config(self, config_window):
        """設定画面の適用"""
        for tab in config_window.widgets:
            if tab in self.settings.config_dict:
                self.settings.config_dict[tab] = MainController.get_new_config(
                    config_window.widgets[tab], self.settings.config_dict[tab]
                )
        self.presets.config_dict[
            "_general_preset"
        ] = MainController.get_new_config(
            config_window.widgets["gen_pre_config_tab"],
            self.presets.config_dict["_general_preset"]
        )

    @staticmethod
    def get_new_config(widgets_dict, config_dict):
        """設定画面の新規値を取得し現在の設定辞書を更新(タブ毎呼び出し前提)"""
        new_dict = {}
        for key in widgets_dict:
            if isinstance(widgets_dict[key], dict):
                new_dict[key] = MainController.get_new_config(
                    widgets_dict[key], config_dict[key]
                )
            else:
                new_val = widgets_dict[key].get()
                if new_val is None:
                    new_dict[key] = config_dict[key]
                else:
                    new_dict[key] = new_val

        return new_dict

    def config_view_set_default(self, config_window):
        """設定画面を開いたあと初期化用値を設定する"""
        MainController.settings_set_default(
            config_window.widgets, self.settings.default_dict
        )
        MainController.preset_set_default(
            config_window.widgets["gen_pre_config_tab"],
            self.presets.default_dict["_general_preset"]
        )

    @staticmethod
    def settings_set_default(widgets_dict, settings_default_dict):
        """設定画面用初期化用値設定(settings編)"""
        for key in widgets_dict:
            if key in settings_default_dict:
                if isinstance(widgets_dict[key], dict):
                    MainController.settings_set_default(
                        widgets_dict[key], settings_default_dict[key]
                    )
                else:
                    widgets_dict[key].set_default(settings_default_dict[key])

    @staticmethod
    def preset_set_default(widgets_dict, preset_default_dict):
        """設定画面用初期化用値設定(preset編)"""
        for key in widgets_dict:
            widgets_dict[key].set_default(preset_default_dict[key])

    def reading_execution_at_main(self):
        # 日付の記述およびファイルの存在をチェック
        for config_unit in self.ui.loading_area.config_unit_list:
            if config_unit:
                date_text = config_unit.date_entry.get()
                is_date = reader_model.check_date(date_text)
                if not is_date:
                    messagebox.showwarning(
                        "エラー",
                        "日付には存在する年月日(YYYY-MM-DD)を半角で入力してください。"
                    )
                    return None
                file_path = config_unit.file_path_label.cget("text")
                path = Path(file_path)
                if not path.exists():
                    messagebox.showwarning(
                        "エラー",
                        f'"{file_path}"は\n存在していません。'
                    )
                    return None
        for df_unit in self.ui.loading_area.df_unit_list:
            if df_unit:
                file_path = df_unit.file_path_label.cget("text")
                path = Path(file_path)
                if not path.exists():
                    messagebox.showwarning(
                        "エラー",
                        f'"{file_path}"は\n存在していません。'
                    )
                    return None

        p_dialog = ProgressDialog(self.ui)

        self.reading_execution_at_sub(p_dialog=p_dialog)

    @decorators.th_deco
    def reading_execution_at_sub(self, p_dialog=None):
        if p_dialog:
            pr_bar = p_dialog.progress_bar
            pr_text = p_dialog.progress_text
            kill_flag = p_dialog.kill_flag
        else:
            pr_bar = ttk.Progressbar(self.ui)
            pr_text = tk.StringVar(self.ui)
            kill_flag = tk.BooleanVar(self.ui, value=False)

        # データフレーム読み込みを実行
        self.initial_reading(p_dialog=p_dialog)

        if kill_flag.get():
            self.storage.clear()
            return None

        pr_bar.config(mode="indeterminate")
        pr_bar.start()
        pr_text.set("グラフ設定中...")

        # 期間取得
        dates_np_list = self.storage.raw_df["date"].unique()
        dates_list = dates_np_list.tolist()
        dates_list.sort(key=lambda x: int(x.replace("-", "")))
        dates_list.insert(0, "")
        self.storage.dates_list = dates_list

        # 各スクリーンの初期設定を反映
        self.s1_set_parameters()
        self.s3_set_parameters()

        if kill_flag.get():
            self.storage.clear()
            return None

        # 各スクリーンのグラフ設定を実行
        self.storage.s1.df = self.storage.raw_df.copy()
        pr_text.set("グラフ設定中...(1/2)")
        self.s1_update_graph()
        pr_text.set("グラフ設定中...(2/2)")
        self.s3_update_graph()

        # 各スクリーンのボタンを設定
        self.s1_set_button_commands()
        self.s3_set_button_commands()

        # 画面を変更
        self.ui.pushed_loading()
        self.root.menu_file.entryconfig(
            0, state=tk.ACTIVE, command=self.change_session_name
        )
        self.root.menu_file.entryconfig(
            1, state=tk.ACTIVE, command=self.restart
        )
        self.root.menu_file.entryconfig(3, command=self.to_quit_application)
        self.root.protocol("WM_DELETE_WINDOW", self.to_quit_application)

        p_dialog.destroy()

    def initial_reading(self, p_dialog=None):
        """データフレームの読み込み"""
        if p_dialog:
            pr_bar = p_dialog.progress_bar
            pr_text = p_dialog.progress_text
            pr_val = p_dialog.progress_val
            kill_flag = p_dialog.kill_flag
        else:
            pr_bar = ttk.Progressbar(self.ui)
            pr_text = tk.StringVar(self.ui)
            pr_val = tk.IntVar(self.ui)
            kill_flag = tk.BooleanVar(self.ui, value=False)

        pr_bar.config(mode="indeterminate")
        pr_bar.start()

        # dfの読み込みを実行
        existing_df_list = []
        existing_df = None
        max_length = 0
        max_name = ""
        pr_text.set("処理済みデータフレーム読込中...")
        for df_unit in self.ui.loading_area.df_unit_list:
            file_path = df_unit.file_path_label.cget("text")
            df = reader_model.read_df_json_file(file_path)
            if self.is_df(df):
                existing_df_list.append(df)
                if len(df.index) > max_length:
                    max_length = len(df.index)
                    max_name = Path(file_path).name
        if existing_df_list:
            existing_df = merger_model.merge_dfs(existing_df_list)

        # フラグチェック
        if kill_flag.get():
            return None

        # テキストファイルの読み込みを実行
        new_df_list = []
        new_df = None
        pr_text.set("テキストファイル読込中...")
        for config_unit in self.ui.loading_area.config_unit_list:
            if config_unit:
                date_str = config_unit.date_entry.get()
                title = config_unit.session_name_entry.get()
                file_path = config_unit.file_path_label.cget("text")
                df = reader_model.read_txt_file(date_str, title, file_path)
                if self.is_df(df):
                    new_df_list.append(df)
                if kill_flag.get():
                    return None
        if new_df_list:
            new_df = merger_model.merge_dfs(new_df_list)

        # フラグチェック
        if kill_flag.get():
            return None

        # 解析前処理
        if self.is_df(new_df) and self.is_df(existing_df):
            new_df = merger_model.compare_new_and_existing_dfs(
                new_df, existing_df
            )

        # 解析処理
        if self.is_df(new_df):
            maximum = len(new_df.index)
            pr_bar.stop()
            pr_bar.config(mode="determinate", maximum=maximum)

            new_df = word_analyser_model.analyse_chats(
                new_df, i_var=pr_val, s_var=pr_text, kill_flag=kill_flag
            )

            if self.is_df(existing_df):
                self.storage.raw_df = merger_model.join_dfs(
                    new_df, existing_df
                )
            else:
                self.storage.raw_df = merger_model.sort_df(new_df)
        else:
            self.storage.raw_df = merger_model.sort_df(existing_df)

        self.storage.s3.dfs["master"] = s3_selector_model.initial_resolve_df(
            self.storage.raw_df
        )

        # session_nameを決定
        if not self.storage.session_name:
            self.storage.session_name = self.storage.raw_df["title"].mode()[0]
        plotter_model.PlotterModel.session_name = self.storage.session_name

        # preset_nameを決定
        if self.storage.session_name in self.presets.config_dict:
            if self.settings.config_dict["io_config_tab"][
                "select_preset_by_session_name"
            ]:
                self.storage.preset_name = self.storage.session_name
        if max_name and max_name in self.presets.config_dict:
            if self.settings.config_dict["io_config_tab"][
                "auto_loading_of_preset"
            ]:
                self.storage.preset_name = max_name

    def s1_set_parameters(self):
        """s1の各パラメータの初期設定をウィジェットに反映"""
        preset_name = self.storage.preset_name
        preset_dict = self.presets.config_dict[preset_name]

        # 期間設定
        self.ui.s1.range_area.start_combobox.config(
            values=self.storage.dates_list
        )
        self.ui.s1.range_area.start_combobox.delete(0, tk.END)
        self.ui.s1.range_area.start_combobox.insert(
            0, preset_dict["s1_range"]["start"]
        )
        self.ui.s1.range_area.end_combobox.config(
            values=self.storage.dates_list
        )
        self.ui.s1.range_area.end_combobox.delete(0, tk.END)
        self.ui.s1.range_area.end_combobox.insert(
            0, preset_dict["s1_range"]["end"]
        )

        # 品詞選択
        for key, value in preset_dict["s1_flags"].items():
            self.ui.s1.flags[key].set(value)

        # ストップワードなど
        self.ui.s1.stopword_entry1.delete(0, tk.END)
        self.ui.s1.stopword_entry1.insert(
            0, str(preset_dict["s1_top_n"])
        )
        self.ui.s1.stopword_entry2.delete(0, tk.END)
        self.ui.s1.stopword_entry2.insert(
            0, str(preset_dict["s1_min_freq"])
        )
        self.ui.s1.stopword_entry3.delete(0, tk.END)
        self.ui.s1.stopword_entry3.insert(
            0, " ".join(preset_dict["s1_ng_words"])
        )
        self.ui.s1.min_freq_entry.delete(0, tk.END)
        self.ui.s1.min_freq_entry.insert(
            0, str(preset_dict["s1_min_edge"])
        )
        self.ui.s1.n_num_var.set(preset_dict["s1_n_num"])

    def _s1_update_parameters(self):
        """入力されている値を読み込んで更新フラグを設定"""
        # 期間
        start_str = self.ui.s1.range_area.start_combobox.get()
        if not reader_model.check_date(start_str):
            start_str = self.ui.s1.range_area.start_combobox.cget("values")[1]
        end_str = self.ui.s1.range_area.end_combobox.get()
        if not reader_model.check_date(end_str):
            end_str = self.ui.s1.range_area.end_combobox.cget("values")[-1]
        if int(start_str.replace("-", "")) > int(end_str.replace("-", "")):
            start_str, end_str = end_str, start_str
        current_range = dict(start=start_str, end=end_str)
        if current_range != self.storage.s1.range:
            self.storage.s1.update_flags["range"] = True
            self.storage.s1.range.update(current_range)

        # s3関連
        self._s3_check_same(self.storage.s1)

        # 品詞など
        current_flags = {}
        for key in self.ui.s1.flags:
            current_flags[key] = self.ui.s1.flags[key].get()
        if current_flags != self.storage.s1.flags:
            self.storage.s1.update_flags["df"] = True
            self.storage.s1.flags.update(current_flags)
        current_ng_words = self.ui.s1.stopword_entry3.get()
        current_ng_words = current_ng_words.split()
        if current_ng_words != self.storage.s1.ng_words:
            self.storage.s1.update_flags["df"] = True
            self.storage.s1.ng_words = current_ng_words

        # ストップワード
        try:
            current_top_n = int(self.ui.s1.stopword_entry1.get())
        except ValueError:
            current_top_n = 0
        try:
            current_min_freq = int(self.ui.s1.stopword_entry2.get())
        except ValueError:
            current_min_freq = 0
        current_stopwords = dict(
            top_n=current_top_n, min_freq=current_min_freq
        )
        if current_stopwords != self.storage.s1.stopwords:
            self.storage.s1.update_flags["stopwords"] = True
            self.storage.s1.stopwords.update(current_stopwords)

        # N-gram
        current_n_num = self.ui.s1.n_num_var.get()
        if current_n_num != self.storage.s1.n_num:
            self.storage.s1.update_flags["n_gram"] = True
            self.storage.s1.n_num = current_n_num

        # 共起ネットワーク
        try:
            current_min_edge = int(self.ui.s1.min_freq_entry.get())
        except ValueError:
            current_min_edge = 0
        if current_min_edge != self.storage.s1.min_edge:
            self.storage.s1.update_flags["co_network"] = True
            self.storage.s1.min_edge = current_min_edge

        return True

    def s1_update_graph(self):
        # 入力項目を確認しstorageの値とupdate_flagsを更新する
        res = self._s1_update_parameters()
        if not res:
            return False

        # update_flagを確認し諸々の更新を実行
        if self.storage.s1.update_flags["range"]:
            self.storage.s1.df = merger_model.pick_range_df(
                df=self.storage.raw_df,
                start=self.storage.s1.range["start"],
                end=self.storage.s1.range["end"]
            )
            if self.ui.s3.same_setting_flag.get():
                self.storage.s1.df = merger_model.pick_names_df(
                    df=self.storage.s1.df, sel_mem=self.storage.s1.sel_mem
                )
                # ここで空なら警告
                if self.storage.s1.df.empty:
                    messagebox.showwarning(
                        "警告",
                        "処理後のデータフレームが空です。対象の選択を正しく行ってください。"
                    )
                    return False
            self.storage.s1.update_flags.update(
                range=False, df=True, n_gram=True
            )

        if self.storage.s1.update_flags["df"]:
            self.storage.s1.df = s1_word_selector_model.select_words(
                df=self.storage.s1.df,
                filter_words=self.storage.s1.ng_words,
                flags=self.storage.s1.flags
            )
            self.storage.s1.plotter = plotter_model.S1PlotterModel(
                df=self.storage.s1.df,
                raw_stopwords=self.storage.s1.stopwords,
                min_edge_frequency=self.storage.s1.min_edge
            )
            self.storage.s1.update_flags.update(
                df=False,
                stopword=False,
                uni_gram=True,
                n_gram=True,
                wordcloud=True,
                co_network=True
            )

        if self.storage.s1.update_flags["stopwords"]:
            self.storage.s1.plotter.set_stopwords(self.storage.s1.stopwords)
            self.storage.s1.update_flags.update(
                stopword=False,
                uni_gram=True,
                n_gram=True,
                wordcloud=True,
                co_network=True
            )

        if self.storage.s1.update_flags["co_network"]:
            try:
                self.storage.s1.plotter.build_co_network(
                    self.storage.s1.min_edge
                )
                self.ui.s1.set_con_parameter(
                    node_size=self.storage.s1.plotter.node_size,
                    edge_size=self.storage.s1.plotter.edge_size
                )
            except ValueError:
                self.ui.s1.warn_failure_of_con_setting()

        return True

    def s1_show_graph(self, graph_type):
        """
        graph_typeで指定されたグラフを表示する

        :param graph_type: グラフの種類(uni_gram, n_gram, wordcloud, co_network)
        """

        if graph_type in self.storage.s1.update_flags:
            res = self.s1_update_graph()
            if not res:
                return False
            if self.storage.s1.update_flags[graph_type]:
                params = self.settings.config_dict["s1_params"][graph_type]
                if graph_type == "n_gram":
                    params = params.copy()
                    params["ngram"] = self.storage.s1.n_num
                self.storage.s1.plotter.get_graph(
                    graph_type=graph_type, params=params
                )

            if graph_type == "wordcloud":
                self.storage.s1.plotter.plot_for_matplotlib(
                    graph_type=graph_type, save=self.ui.html_save_flag.get()
                )
            else:
                self.storage.s1.plotter.plot_for_plotly(
                    graph_type=graph_type, save=self.ui.html_save_flag.get(),
                    graph_config=self.settings.config_dict["graph_config_tab"]
                )

    def s1_open_dataframe_view(self):
        res = self.s1_update_graph()
        if res:
            DataFrameView(self.root, df=self.storage.s1.df, mode=1)

    def s1_set_button_commands(self):
        self.ui.s1.df_update_button.config(command=self.s1_update_graph)
        self.ui.s1.df_button.config(command=self.s1_open_dataframe_view)
        self.ui.s1.uni_gram_button.config(
            command=lambda: self.s1_show_graph("uni_gram")
        )
        self.ui.s1.n_gram_button.config(
            command=lambda: self.s1_show_graph("n_gram")
        )
        self.ui.s1.wordcloud_button.config(
            command=lambda: self.s1_show_graph("wordcloud")
        )
        self.ui.s1.con_button.config(
            command=lambda: self.s1_show_graph("co_network")
        )

    def s3_set_parameters(self):
        """s3の各パラメータの初期設定をウィジェットに反映"""
        preset_name = self.storage.preset_name
        preset_dict = self.presets.config_dict[preset_name]

        # 期間設定
        self.ui.s3.range_area.start_combobox.config(
            values=self.storage.dates_list
        )
        self.ui.s3.range_area.start_combobox.delete(0, tk.END)
        self.ui.s3.range_area.start_combobox.insert(
            0, preset_dict["s3_range"]["start"]
        )
        self.ui.s3.range_area.end_combobox.config(
            values=self.storage.dates_list
        )
        self.ui.s3.range_area.end_combobox.delete(0, tk.END)
        self.ui.s3.range_area.end_combobox.insert(
            0, preset_dict["s3_range"]["end"]
        )

        # メンバーセレクト設定
        members_np_list = self.storage.raw_df["name"].unique()
        members_list = members_np_list.tolist()
        self.storage.s3.raw_members = members_list
        self.storage.s3.custom_dict = preset_dict["s3_custom_dict"].copy()
        self.storage.s3.sel_custom = preset_dict["s3_sel_custom"].copy()
        # presetにのみ存在するnameがあれば排除する
        difference_set = set(preset_dict["s3_raw_members"]) - set(members_list)
        if difference_set and self.storage.s3.custom_dict:
            for key in list(self.storage.s3.custom_dict):
                self.storage.s3.custom_dict[key] = list(
                    set(self.storage.s3.custom_dict[key]) - difference_set
                )
                if not self.storage.s3.custom_dict[key]:
                    del self.storage.s3.custom_dict[key]
        # カスタムを反映し表示
        s3_selector_model.selection_info_update(
            self.storage.s3, new_cus_dict=self.storage.s3.custom_dict
        )
        self.ui.s3.list_var.set(self.storage.s3.custom_members)
        # セレクト設定を反映
        self.ui.s3.listbox.select_clear(0, tk.END)
        if not self.storage.s3.sel_custom:
            self.storage.s3.sel_custom = self.storage.s3.custom_members
        for i in range(len(self.storage.s3.custom_members)):
            if self.storage.s3.custom_members[i] in self.storage.s3.sel_custom:
                self.ui.s3.listbox.select_set(i)
        self.ui.s3.same_setting_flag.set(preset_dict["s3_same_setting_flag"])

    def _s3_update_parameters(self):
        """入力されている値を読み込んで更新フラグを設定"""
        # 期間
        start_str = self.ui.s3.range_area.start_combobox.get()
        if not reader_model.check_date(start_str):
            start_str = self.ui.s3.range_area.start_combobox.cget("values")[1]
        end_str = self.ui.s3.range_area.end_combobox.get()
        if not reader_model.check_date(end_str):
            end_str = self.ui.s3.range_area.end_combobox.cget("values")[-1]
        if int(start_str.replace("-", "")) > int(end_str.replace("-", "")):
            start_str, end_str = end_str, start_str
        current_range = dict(start=start_str, end=end_str)
        if current_range != self.storage.s3.range:
            self.storage.s3.update_flags["range"] = True
            self.storage.s3.range.update(current_range)

        # 選択　※カスタム系を更新した場合、都度フラグをTrueにする
        selection = self.ui.s3.listbox.curselection()
        current_sel = [
            self.storage.s3.custom_members[i] for i in selection
        ]
        new_sel_cus = None
        if set(current_sel) != set(self.storage.s3.sel_custom):
            self.storage.s3.update_flags["df"] = True
            new_sel_cus = current_sel
        s3_selector_model.selection_info_update(
            self.storage.s3, new_sel_cus=new_sel_cus
        )

    def _s3_check_same(self, storage):
        if self.ui.s3.same_setting_flag.get():
            self._s3_update_parameters()
            if set(storage.sel_mem) != set(self.storage.s3.sel_raw):
                storage.sel_mem = self.storage.s3.sel_raw
                storage.update_flags["range"] = True
            elif not self.storage.s3.sel_raw:
                storage.update_flags["range"] = True
        else:
            if storage.sel_mem:
                storage.sel_mem.clear()
                storage.update_flags["range"] = True

    def s3_update_graph(self):
        # 入力項目を確認しstorageの値とupdate_flagsを更新する
        self._s3_update_parameters()

        # update_flagを確認し諸々の更新を実行
        if self.storage.s3.update_flags["df"]:
            self.storage.s3.dfs["custom"] = s3_selector_model.make_custom_df(
                df=self.storage.s3.dfs["master"],
                sel_custom=self.storage.s3.sel_custom,
                custom_dict=self.storage.s3.custom_dict
            )
            self.storage.s3.update_flags.update(dict(df=False, range=True))

        if self.storage.s3.update_flags["range"]:
            self.storage.s3.dfs["each"] = merger_model.pick_range_df(
                df=self.storage.s3.dfs["custom"],
                start=self.storage.s3.range["start"],
                end=self.storage.s3.range["end"],
                mode=1
            )
            self.storage.s3.dfs["total"] = s3_selector_model.make_total_df(
                self.storage.s3.dfs["each"]
            )
            self.storage.s3.plotter = plotter_model.S3PlotterModel(
                each_df=self.storage.s3.dfs["each"],
                total_df=self.storage.s3.dfs["total"]
            )
            self.storage.s3.update_flags.update(
                dict(range=False, each=True, total=True)
            )

    def s3_show_graph(self, graph_type):
        """
        graph_typeで指定されたグラフを表示する
        :param graph_type: グラフの種類(each, total)
        """
        if graph_type in self.storage.s3.update_flags:
            self.s3_update_graph()
            if self.storage.s3.update_flags[graph_type]:
                params = self.settings.config_dict["s3_params"][graph_type]
                self.storage.s3.plotter.get_graph(
                    graph_type=graph_type, params=params
                )

        self.storage.s3.plotter.plot_for_plotly(
            graph_type=graph_type, save=self.ui.html_save_flag.get(),
            graph_config=self.settings.config_dict["graph_config_tab"]
        )

    def s3_open_dataframe_view(self, mode):
        self.s3_update_graph()
        DataFrameView(self.root, self.storage.s3.dfs[mode])

    def s3_open_advanced_setting(self):
        mads = MemActsDetailSelectionToplevel(
            self.root,
            name_list=self.storage.s3.raw_members,
            custom_dict=self.storage.s3.custom_dict
        )
        mads.ok_button.config(
            command=lambda: self.s3_reflect_advanced_setting(mads=mads)
        )

    def s3_reflect_advanced_setting(self, mads):
        """詳細画面でOKを押した時にcustom_dictなどを更新"""
        self._s3_update_parameters()

        # 詳細画面での最終設定をdict化
        cus_d = {}
        for isu in mads.isu_list:
            name = isu.name_entry.get()
            inu_list = isu.inu_list
            n_list = [inu_list[i].cb.get() for i in range(len(inu_list))]
            n_list = [mem for mem in n_list if mem]
            if len(n_list) == 0:
                continue
            if not name:
                name = n_list[0]
            # エラー処理
            if name in cus_d:
                messagebox.showerror("エラー", "名前が重複しています。再設定して下さい。")
                return None
            cus_d[name] = list(set(n_list))

        # custom_dictとdictの比較
        if set(cus_d) == set(self.storage.s3.custom_dict):
            for key in cus_d:
                if set(cus_d[key]) != set(self.storage.s3.custom_dict[key]):
                    self.storage.s3.update_flags["df"] = True
        else:
            self.storage.s3.update_flags["df"] = True

        # 比較の結果相違であれば更新メソッドを実行
        if self.storage.s3.update_flags["df"]:
            s3_selector_model.selection_info_update(self.storage.s3, cus_d)
            self.ui.s3.list_var.set(self.storage.s3.custom_members)

        # 選択状況を更新
        self.ui.s3.listbox.select_clear(0, tk.END)
        for i in range(len(self.storage.s3.custom_members)):
            if self.storage.s3.custom_members[i] in self.storage.s3.sel_custom:
                self.ui.s3.listbox.select_set(i)

        mads.destroy()

    def s3_set_button_commands(self):
        self.ui.s3.advanced_setting_button.config(
            command=self.s3_open_advanced_setting
        )
        self.ui.s3.df_button1.config(
            command=lambda: self.s3_open_dataframe_view("each")
        )
        self.ui.s3.df_button2.config(
            command=lambda: self.s3_open_dataframe_view("total")
        )
        self.ui.s3.each_day_graph_button.config(
            command=lambda: self.s3_show_graph("each")
        )
        self.ui.s3.all_day_graph_button.config(
            command=lambda: self.s3_show_graph("total")
        )

    def to_quit_application(self):
        self._s1_update_parameters()
        self._s3_update_parameters()

        quit_ok = io_model.export_df_and_presets(
            storage=self.storage,
            presets=self.presets,
            settings=self.settings,
            s3_same_f=self.ui.s3.same_setting_flag.get(),
            auto=self.settings.config_dict["io_config_tab"]["df_auto_save"]
        )

        if quit_ok:
            self.root.destroy()

        return quit_ok

    def restart(self):
        rerun(self)


def run():
    root = MainWindow()
    MainController(root)
    root.mainloop()


def rerun(app):
    re_ok = messagebox.askokcancel("確認", "読み込み画面に戻ります。よろしいですか？")
    if re_ok:
        if app.to_quit_application():
            run()


if __name__ == "__main__":
    run()
