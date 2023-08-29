import tkinter as tk
from tkinter import ttk


class ScrollableFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        # 直下のアイテムを作成・配置
        self.canvas = tk.Canvas(self, bd=0)
        self.x_scrollbar = ttk.Scrollbar(
            self, orient=tk.HORIZONTAL, command=self.canvas.xview
        )
        self.y_scrollbar = ttk.Scrollbar(
            self, orient=tk.VERTICAL, command=self.canvas.yview
        )
        self.y_scrollbar.pack(side=tk.RIGHT, expand=True, fill=tk.Y)
        self.x_scrollbar.pack(side=tk.BOTTOM, expand=True, fill=tk.X)
        self.canvas.pack()

        # スクロール関連の設定
        self.canvas.config(
            scrollregion=(0, 0, 1, 1),
            xscrollcommand=self.x_scrollbar.set,
            yscrollcommand=self.y_scrollbar.set
        )
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)

        # 内部フレームの作成
        self.main_frame = ttk.Frame(self.canvas)
        self.canvas.create_window(0, 0, anchor=tk.NW, window=self.main_frame)

        # 大きさの制御を設定
        self.main_frame.bind("<Configure>", self._mod_canvas_size)

    def _mod_canvas_size(self, event):
        self.canvas.config(
            scrollregion=(
                0, 0,
                max(1, self.main_frame.winfo_reqwidth()),
                max(1, self.main_frame.winfo_reqheight())
            ),
            width=self.main_frame.winfo_reqwidth(),
            height=self.main_frame.winfo_reqheight()
        )
