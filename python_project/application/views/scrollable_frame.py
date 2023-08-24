import tkinter as tk
from tkinter import ttk


class ScrollableFrame(ttk.Frame):
    """
    スクロールバー付きフレーム
    下記サイトのコードを一部改変
    url: https://zenn.dev/dri_cro_6663/articles/0fb9560f6944e2
    """
    def __init__(self, parent, size=(1, 1), fit_w=False, fit_h=False):
        """
        parent: tk.Frame
            親となるフレーム
        minimal_size: tuple
            最小キャンバスサイズ
        fit_w: bool
            キャンバス内のフレームの幅をキャンバスに合わせるか否か
        fit_h: bool
            キャンバス内のフレームの高さをキャンバスに合わせるか否か
        """
        ttk.Frame.__init__(self, parent)

        # 変数の初期化
        self.minimal_canvas_size = size
        self.fit_width = fit_w
        self.fit_height = fit_h

        # 縦スクロールバー
        self.vscrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL)
        self.vscrollbar.pack(fill=tk.Y, side=tk.RIGHT, expand=False)
        # 横スクロールバー
        self.hscrollbar = ttk.Scrollbar(self, orient=tk.HORIZONTAL)
        self.hscrollbar.pack(fill=tk.X, side=tk.BOTTOM, expand=False)
        # Canvas
        self.canvas = tk.Canvas(
            self, bd=0, highlightthickness=0,
            yscrollcommand=self.vscrollbar.set,
            xscrollcommand=self.hscrollbar.set
        )
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # スクロールバーを Canvas に関連付け
        self.vscrollbar.config(command=self.canvas.yview)
        self.hscrollbar.config(command=self.canvas.xview)
        # Canvas の位置の初期化
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)
        # スクロール範囲の設定
        self.canvas.config(
            scrollregion=(
            0, 0, self.minimal_canvas_size[0], self.minimal_canvas_size[1])
        )

        # Canvas 内にフレーム作成
        self.interior = ttk.Frame(self.canvas)
        self.interior_id = self.canvas.create_window(
            0, 0, window=self.interior, anchor=tk.NW,
        )

        # 内部フレームの大きさが変わったらCanvasの大きさを変える関数を呼び出す
        self.canvas.bind('<Configure>', self._configure_canvas)
        # self.canvas.bind_all(sequence="<MouseWheel>",
        #                      func=self._on_mousewheel, add="+")
        self.interior.bind('<Configure>', self._configure_interior)

    def bind_child(self, frame, sequence, func, add=""):
        """
        入れ子に bind を設定

        Parameters
        ----------
        frame: tk.Frame
            bind を設定するフレーム
        sequence: str
            イベント内容
        func: function
            イベント内容が実行された場合に呼ばれる関数
        add: str
            一つ前に宣言されるbind関数を実行するのか設定
            "": default, "+"
        """
        children = frame.winfo_children()
        for child in children:
            c_type = type(child)
            if (c_type == tk.Canvas) or (c_type == tk.Frame) or (
                    c_type == ttk.Frame):
                self.bind_child(frame=child, sequence=sequence, func=func,
                                add=add)
            child.bind(sequence=sequence, func=func, add=add)

    def update_minimal_canvas_size(self, size):
        """
        Parameters
        ----------
        size: tuple
            最小キャンバスサイズ
        """
        self.minimal_canvas_size = size

    def destroy_child(self, frame=None):
        """
        入れ子のウィジェットを削除

        Parameters
        ----------
        frame: tk.Frame
            親となるフレーム
        """
        for child in frame.winfo_children():
            child.destroy()

    def _configure_interior(self, event):
        """
        Canvas の大きさを変える関数

        Parameters
        ----------
        event
            実行される関数の引数へ付与されるイベント情報
        """
        size = (
            max(self.interior.winfo_reqwidth(), self.minimal_canvas_size[0]),
            max(self.interior.winfo_reqheight(), self.minimal_canvas_size[1])
        )
        self.canvas.config(scrollregion=(0, 0, size[0], size[1]))
        if self.interior.winfo_reqwidth() != self.canvas.winfo_width():
            self.canvas.config(width=self.interior.winfo_reqwidth())
        if self.interior.winfo_reqheight() != self.canvas.winfo_height():
            self.canvas.config(height=self.interior.winfo_reqheight())

    def _configure_canvas(self, event):
        """
        Canvas 内のアイテムの大きさを変える関数

        Parameters
        ----------
        event
            実行される関数の引数へ付与されるイベント情報
        """
        interior_reqwidth = self.interior.winfo_reqwidth()
        canvas_width = self.canvas.winfo_width()
        if (interior_reqwidth != canvas_width) and self.fit_width:
            # update the inner frame's width to fill the canvas
            self.canvas.itemconfigure(self.interior_id, width=canvas_width)
        interior_reqheight = self.interior.winfo_reqheight()
        canvas_height = self.canvas.winfo_height()
        if (interior_reqheight != canvas_height) and self.fit_height:
            # update the inner frame's height to fill the canvas
            self.canvas.itemconfigure(self.interior_id, height=canvas_height)

    def _on_mousewheel(self, event=None):
        """
        キャンバスの Y スクロールとマウスホイールスクロールを関連付け

        Parameters
        ----------
        event
            実行される関数の引数へ付与されるイベント情報
        """
        # if event: self.canvas.yview_scroll(int(-1*(event.delta//120)),
        #                                    'units')
        if event:
            self.canvas.yview_scroll(
                int(-1 * (event.delta / abs(event.delta))), "units")
