import threading
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk


class ProgressDialog(tk.Toplevel):
    def __init__(self, master=None, title="処理中"):
        super().__init__(master)

        self.title(title)
        self.kill_flag = tk.BooleanVar(self, value=False)

        # モーダル化
        self.grab_set()
        self.focus_set()
        self.lift()
        self.transient(master)

        # ×ボタンの挙動を設定
        self.protocol("WM_DELETE_WINDOW", self.canceled)

        label = tk.Label(self, text="処理を実行しています。\nしばらくお待ちください。")

        progress_frame = tk.Frame(self)
        self.progress_text = tk.StringVar(self)
        progress_label = tk.Label(
            progress_frame, textvariable=self.progress_text
        )
        self.progress_val = tk.IntVar(self, value=0)
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            length=200,
            mode="determinate",
            orient=tk.HORIZONTAL,
            variable=self.progress_val
        )

        label.pack(pady=10)
        progress_frame.pack(padx=10, pady=10)
        progress_label.pack(anchor=tk.W)
        self.progress_bar.pack()

        self.cancel_button = ttk.Button(
            self, text="キャンセル", command=self.canceled
        )
        self.cancel_button.pack(side=tk.BOTTOM, pady=10)

    def canceled(self):
        is_ok = messagebox.askokcancel(
            title="確認",
            message="実行中の処理を中止しますか？"
        )
        if is_ok:
            self.cancel_button.config(state=tk.DISABLED)
            self.protocol("WM_DELETE_WINDOW", blank_func)

            if self.progress_bar.cget("mode") == "indeterminate":
                self.progress_bar.stop()

            self.kill_flag.set(True)

            ac = threading.active_count()
            while ac > 1:
                self.update()
                ac = threading.active_count()

            self.destroy()


def blank_func():
    pass


# テスト用
if __name__ == "__main__":
    root = tk.Tk()
    pd = ProgressDialog(root)
    pd.progress_text.set("解析中...(40/100)")
    pd.progress_val.set(40)

    root.mainloop()
