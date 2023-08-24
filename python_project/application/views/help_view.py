from pathlib import Path
import tkinter as tk
from tkinter import ttk


FRAME_WIDTH = 490

def activate_help_window(master):
    p = Path(__file__).parent.parent.parent.joinpath("read_me.txt")
    HelpToplevel(master, p)


class HelpToplevel(tk.Toplevel):
    def __init__(self, master, read_me_path):
        super().__init__(master)

        self.title("マニュアル")
        self.lift()
        self.focus_set()

        self.create_widgets(read_me_path)

    def create_widgets(self, read_me_path):
        # 下部ボタン領域の設定
        close_button = ttk.Button(
            self, text="閉じる", command=self.destroy
        )
        close_button.pack(side=tk.BOTTOM, anchor=tk.E, padx=5, pady=2)

        # ヘルプ表示領域の設定
        main_notebook = ttk.Notebook(self)
        main_notebook.pack(anchor=tk.W, padx=5, pady=5)

        tabs_dict = {}
        tab_name = ""
        text = ""
        if read_me_path.exists():
            with open(read_me_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line[0] == "■":
                        if tab_name:
                            tabs_dict[tab_name].set(text)
                            tab_name = ""
                    elif line[0] == "○":
                        if tab_name:
                            tabs_dict[tab_name].set(text)
                        text = ""
                        tab_name = line[1:-1]
                        tabs_dict[tab_name] = OneTabFrame(main_notebook)
                        main_notebook.add(tabs_dict[tab_name], text=tab_name)
                    else:
                        text += line
                if tab_name:
                    tabs_dict[tab_name].set(text)


class OneTabFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master, width=FRAME_WIDTH, height=600)
        self.pack_propagate(False)

        self.canvas = tk.Canvas(self)
        self.frame = tk.Frame(self.canvas)
        self.label = tk.Label(
            self.frame, wraplength=FRAME_WIDTH-30, justify=tk.LEFT
        )
        self.scrollbar = ttk.Scrollbar(
            self.canvas, orient=tk.VERTICAL, command=self.canvas.yview
        )
        self.canvas.config(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(expand=True, fill=tk.BOTH)
        self.label.pack(anchor=tk.W)

        self.canvas.create_window((0.0, 0.0), window=self.frame, anchor=tk.NW)

    def set(self, text):
        self.label.config(text=text)
        reqheight = self.label.winfo_reqheight()
        self.canvas.config(scrollregion=(0, 0, FRAME_WIDTH-20, reqheight))
        if reqheight > 550:
            self.label.bind("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, event=None):
        """キャンバスの Y スクロールとマウスホイールスクロールを関連付け"""
        if event:
            self.canvas.yview_scroll(
                int(-1 * (event.delta / abs(event.delta))), "units")


if __name__ == "__main__":
    root = tk.Tk()

    button = tk.Button(root, text="展開", command=lambda: activate_help_window(root))
    button.pack(padx=20, pady=10)

    root.mainloop()
