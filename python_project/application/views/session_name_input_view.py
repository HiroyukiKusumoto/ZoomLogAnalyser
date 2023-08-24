import tkinter as tk
from tkinter import ttk

try:
    from .validate_commands import ValidateCommands
except ImportError:
    from validate_commands import ValidateCommands


class SessionNameInputView(tk.Toplevel):
    def __init__(self, master, session_name=""):
        super().__init__(master)
        self.result = None

        self.title("ミーティング名の変更")
        self.lift()

        # モーダル化
        self.grab_set()
        self.focus_set()
        self.transient(master)

        vcmd = ValidateCommands(filename=True)

        label = tk.Label(self, text="ミーティング名を入力(Enterで更新)")
        label.pack(anchor=tk.W)

        entry = ttk.Entry(
            self, width=30, validate="key",
            validatecommand=(vcmd.filename, "%P")
        )
        entry.pack()
        entry.insert(0, session_name)
        entry.bind("<Key-Return>", self.update_result)
        entry.focus_set()

    def update_result(self, event):
        """Enterが押された時の処理"""
        self.result = event.widget.get()
        if not self.result:
            self.result = None
        self.destroy()


if __name__ == "__main__":
    root = tk.Tk()

    def activate_window():
        sni = SessionNameInputView(root, "testtesttest")
        root.wait_window(sni)
        print(sni.result)

    button = tk.Button(root, text="展開", command=activate_window)
    button.pack(padx=20, pady=10)

    root.mainloop()
