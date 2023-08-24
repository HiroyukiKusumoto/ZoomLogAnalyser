"""解析中のデータフレームの参照先クラスおよび読み書き処理"""


class DFTempStorage(object):
    def __init__(self):
        # 以下、参照済
        self.dir_path = None
        self.session_name = None
        self.preset_name = "_general_preset"
        self.raw_df = None
        self.dates_list = []
        self.s1 = S1DFTempStorage()
        self.s2 = S2DFTempStorage()
        self.s3 = S3DFTempStorage()

    def export_df(self, file_path):
        self.raw_df.to_json(
            str(file_path), orient="records", force_ascii=False, indent=4
        )

    def clear(self):
        self.__init__()


class S1DFTempStorage(object):
    def __init__(self):
        self.df = None

        self.range = dict(start="", end="")
        self.flags = dict()
        self.stopwords = dict(top_n=0, min_freq=0)
        self.ng_words = []
        self.min_edge = 0
        self.n_num = 2
        self.sel_mem = []

        self.plotter = None

        self.update_flags = dict(
            range=True,
            df=True,
            stopwords=True,
            uni_gram=True,
            n_gram=True,
            wordcloud=True,
            co_network=True
        )


class S2DFTempStorage(object):
    def __init__(self):
        self.dfs = dict(
            master=None,
            word=dict(
                each=None,
                total=None
            ),
            hinshi=dict(
                each=None,
                total=None
            )
        )

        self.range = dict(start="", end="")
        self.selection_dicts = dict(word={}, hinshi={})

        self.update_flags = dict(
            range=True,
            master_df=True,
            word=dict(
                df=True,
                each=True,
                total=True
            ),
            hinshi=dict(
                df=True,
                each=True,
                total=True
            )
        )


class S3DFTempStorage(object):
    def __init__(self):
        self.dfs = dict(
            master=None,
            custom=None,
            each=None,
            total=None
        )

        self.range = dict(start="", end="")
        self.raw_members = []
        self.custom_members = []
        self.custom_dict = dict()
        self.sel_custom = []
        self.sel_raw = []

        self.plotter = None

        self.update_flags = dict(
            range=True,
            df=True,
            each=True,
            total=True
        )
