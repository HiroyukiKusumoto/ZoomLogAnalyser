import tkinter as tk
from tkinter import ttk

try:
    from .validate_commands import ValidateCommands
except ImportError:
    from validate_commands import ValidateCommands


class RangeArea(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)

        self.vcmd = ValidateCommands(date_hyphen=True)

        self.range_label = tk.Label(self, text="集計範囲")
        self.start_combobox = ttk.Combobox(
            self, width=10,
            validate="key", validatecommand=(self.vcmd.date_hyphen, "%P")
        )
        self.between_label = tk.Label(self,text="-")
        self.end_combobox = ttk.Combobox(
            self, width=10,
            validate="key", validatecommand=(self.vcmd.date_hyphen, "%P")
        )

        self.range_label.pack(anchor=tk.W)
        self.end_combobox.pack(side=tk.RIGHT)
        self.between_label.pack(side=tk.RIGHT, padx=5)
        self.start_combobox.pack(side=tk.RIGHT)


if __name__ == "__main__":
    root = tk.Tk()
    range_area = RangeArea(root)
    range_area.pack(padx=10, pady=10)

    root.mainloop()
