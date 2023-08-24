from datetime import datetime
from pathlib import Path
import tempfile
import time
from tkinter import filedialog
from tkinter import messagebox
import webbrowser

import nlplot
import pandas as pd
from plotly.offline import plot
import matplotlib.pyplot as plt

try:
    from . import decorators
except ImportError:
    import decorators


UNI_GRAM_PARAMS = dict(
    title="uni-gram",
    xaxis_label="word_count",
    yaxis_label="word"
)
N_GRAM_PARAMS = dict(
    title="N-gram",
    xaxis_label="word_count",
    yaxis_label="word",
    ngram=1
)
CO_NETWORK_PARAMS = dict(
    title="Co-occurrence network",
    sizing=100,
    node_size="adjacency_frequency",
    color_palette="hls",
    width=1100,
    height=700
)
BAR_PARAMS = dict(
    title="by word",
    template="plotly_white",
    labels=dict(index="word", value="number")
)
EACH_DAY_BAR_PARAMS = dict(
    title="by word",
    template="plotly_white",
    labels=dict(index="date", value="number")
)
EACH_AGGREGATED_PARAMS = dict(
    title="number of comments",
    template="plotly_white",
    labels=dict(index="date",
                value="number of comments",
                variable="members")
)
TOTAL_AGGREGATED_PARAMS = dict(
    title="number of comments(total)",
    template="plotly_white",
    labels=dict(index="date",
                value="number of comments(total)",
                variable="members")
)


class PlotterModel(object):
    wait_time = 3
    save_path = None
    plt_fig_format = "png"
    overwrite_flag = False
    session_name = ""

    def __init__(self):
        self.figs = {}

    def plot_for_plotly(self, graph_type, graph_config, save=False):
        if save:
            self.plot_for_plotly_with_saving(graph_type, graph_config)
        else:
            self.plot_for_plotly_with_temp(graph_type, graph_config)

    @decorators.th_deco
    def plot_for_plotly_with_temp(self, graph_type, graph_config):
        with tempfile.TemporaryDirectory() as tempdir:
            path = Path(tempdir)
            filename = str(path.joinpath(f"{graph_type}.html"))
            plot(
                self.figs[graph_type],
                filename=filename,
                auto_open=False,
                config=dict(
                    edits=dict(
                        axisTitleText=graph_config["graph_labels_editable"],
                        legendPosition=graph_config["graph_legend_movable"],
                        legendText=graph_config["graph_labels_editable"],
                        titleText=graph_config["graph_labels_editable"]
                    ),
                    scrollZoom=graph_config["scroll_zoom"]
                )
            )
            webbrowser.open(filename)
            time.sleep(self.wait_time)

    @decorators.th_deco
    def plot_for_plotly_with_saving(self, graph_type, graph_config):
        if self.save_path:
            save_dir = Path(self.save_path)
            if not save_dir.exists():
                save_dir.mkdir(parents=True, exist_ok=True)
            now_dt = datetime.now()
            now_str = now_dt.strftime("%Y%m%d_%H%M%S")
            save_path = save_dir.joinpath(
                f"{now_str}_{graph_type}_{self.session_name}.html"
            )
        else:
            save_path_str = filedialog.asksaveasfilename(
                title="名前を付けて保存",
                filetypes=[("htmlファイル", ".html")],
                defaultextension="html"
            )
            if not save_path_str:
                return None
            save_path = Path(save_path_str)

        if save_path.exists() and not self.overwrite_flag:
            res = messagebox.askokcancel(
                "確認", f'"{save_path.name}"は存在しています。\n上書きしますか？'
            )
            if not res:
                return None

        filename = str(save_path)
        plot(
            self.figs[graph_type],
            filename=filename,
            auto_open=False,
            config=dict(
                edits=dict(
                    axisTitleText=graph_config["graph_labels_editable"],
                    legendPosition=graph_config["graph_legend_movable"],
                    legendText=graph_config["graph_labels_editable"],
                    titleText=graph_config["graph_labels_editable"]
                ),
                scrollZoom=graph_config["scroll_zoom"]
            )
        )
        webbrowser.open(filename)

    def plot_for_matplotlib(self, graph_type, save=False):
        plt.figure(figsize=(16, 12))
        plt.imshow(self.figs[graph_type], interpolation="bilinear")
        plt.axis("off")

        if save:
            f_format = self.plt_fig_format
            if self.save_path:
                save_dir = Path(self.save_path)
                if not save_dir.exists():
                    save_dir.mkdir(parents=True, exist_ok=True)
                now_dt = datetime.now()
                now_str = now_dt.strftime("%Y%m%d_%H%M%S")
                save_path = save_dir.joinpath(
                    f"{now_str}_{graph_type}_{self.session_name}.{f_format}"
                )
            else:
                save_path_str = filedialog.asksaveasfilename(
                    title="名前を付けて保存",
                    filetypes=[(f"{f_format}ファイル", f".{f_format}")],
                    defaultextension=f_format
                )
                if not save_path_str:
                    return None
                save_path = Path(save_path_str)

            if save_path.exists() and not self.overwrite_flag:
                res = messagebox.askokcancel(
                    "確認", f'"{save_path.name}"は存在しています。\n上書きしますか？'
                )
                if not res:
                    return None
            plt.savefig(str(save_path), format=f_format)

        plt.show()


class S1PlotterModel(PlotterModel):
    """設定したデータフレームからNLPlotを用いてグラフの作成を行う"""
    def __init__(self, df, raw_stopwords=None, min_edge_frequency=1):
        super().__init__()
        if raw_stopwords is None:
            raw_stopwords = dict(top_n=0, min_freq=0)

        self.npt = nlplot.NLPlot(df, target_col="words")
        self.all_npt = nlplot.NLPlot(df, target_col="all_words")
        self.node_size = 0
        self.edge_size = 0
        self.stopwords = None
        self.all_stopwords = None

        self.figs.update(
            uni_gram=None, n_gram=None, wordcloud=None, co_network=None
        )

        # ストップワードの設定
        self.set_stopwords(raw_stopwords)

        # co-networkの構築
        self.build_co_network(min_edge_frequency=min_edge_frequency)

    def set_stopwords(self, raw_stopwords):
        """ストップワードを設定"""
        self.stopwords = self.npt.get_stopword(
            top_n=raw_stopwords["top_n"], min_freq=raw_stopwords["min_freq"]
        )
        self.all_stopwords = self.all_npt.get_stopword(
            top_n=raw_stopwords["top_n"], min_freq=raw_stopwords["min_freq"]
        )

    @decorators.redirect_deco
    def build_co_network(self, min_edge_frequency):
        """共起ネットワークを構築"""
        self.npt.build_graph(stopwords=self.stopwords,
                             min_edge_frequency=min_edge_frequency)

        # ノード数とエッジ数をtkinterで表示するために値を取得
        self.node_size = self.npt.node_df.shape[0]
        self.edge_size = self.npt.edge_df.shape[0]

    def get_graph(self, graph_type, params=None):
        """渡されたgraph_typeに応じたグラフに更新"""
        if graph_type in self.figs:
            fig = None
            if graph_type == "uni_gram":
                fig = self.make_uni_gram(params)
            elif graph_type == "n_gram":
                fig = self.make_n_gram(params)
            elif graph_type == "wordcloud":
                fig = self.make_wordcloud()
            elif graph_type == "co_network":
                fig = self.make_co_network(params)

            self.figs[graph_type] = fig

    def make_uni_gram(self, params=None):
        """uni_gramを作成"""
        if params is None:
            params = {}
        uni_gram_params = UNI_GRAM_PARAMS | params

        fig_uni_gram = self.npt.bar_ngram(
            ngram=1, stopwords=self.stopwords, verbose=False, **uni_gram_params
        )

        return fig_uni_gram

    def make_n_gram(self, params=None):
        """n_gramを作成"""
        if params is None:
            params = {}
        n_gram_params = N_GRAM_PARAMS | params

        fig_n_gram = self.all_npt.bar_ngram(
            stopwords=self.all_stopwords, verbose=False, **n_gram_params
        )

        return fig_n_gram

    def make_wordcloud(self):
        """ワードクラウドを作成"""
        fig_wc = self.npt.wordcloud(stopwords=self.stopwords)

        return fig_wc

    def make_co_network(self, params=None):
        """共起ネットワークを作成"""
        if params is None:
            params = {}
        co_network_params = CO_NETWORK_PARAMS | params

        fig_co_network = self.npt.co_network(**co_network_params)

        return fig_co_network


class S3PlotterModel(PlotterModel):
    """設定したデータフレームからplotlyで折れ線グラフの作成を行う"""
    def __init__(self, each_df, total_df):
        super().__init__()
        self.each_df = each_df
        self.total_df = total_df
        pd.options.plotting.backend = "plotly"

        self.figs.update(each=None, total=None)

    def get_graph(self, graph_type, params=None):
        """渡されたgraph_typeに応じたグラフに更新"""
        if graph_type in self.figs:
            fig = None
            if graph_type == "each":
                fig = self.make_each_graph(params)
            elif graph_type == "total":
                fig = self.make_total_graph(params)

            self.figs[graph_type] = fig

    def make_each_graph(self, params=None):
        if params is None:
            params = {}
        each_params = EACH_AGGREGATED_PARAMS | params

        fig_each_graph = self.each_df.plot(**each_params)
        fig_each_graph.update_traces(mode="lines+markers")
        fig_each_graph.update_yaxes(range=(0, self.each_df.max().max()+2))
        fig_each_graph.update_xaxes(tickvals=list(self.each_df.index))

        return fig_each_graph

    def make_total_graph(self, params=None):
        if params is None:
            params = {}
        total_params = TOTAL_AGGREGATED_PARAMS | params

        fig_total_graph = self.total_df.plot(**total_params)
        fig_total_graph.update_traces(mode="lines+markers")
        fig_total_graph.update_yaxes(range=(0, self.total_df.max().max() + 2))
        fig_total_graph.update_xaxes(tickvals=list(self.total_df.index))

        return fig_total_graph
