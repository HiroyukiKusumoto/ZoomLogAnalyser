import tkinter as tk
from tkinter import ttk

try:
    from .scrollable_frame import ScrollableFrame
except ImportError:
    from scrollable_frame import ScrollableFrame


class MemActsDetailSelectionToplevel(tk.Toplevel):
    def __init__(self, master, name_list=None, custom_dict=None):
        super().__init__(master)

        self.title("発言者の詳細選択")
        self.lift()

        # モーダル化
        self.grab_set()
        self.focus_set()
        self.transient(master)

        if name_list is None:
            self.name_list = []
        else:
            self.name_list = name_list.copy()
        self.name_list.insert(0, "")
        self.isu_list = []

        # ボタン領域の設定
        self.button_area = tk.Frame(self)
        self.button_area.pack(side=tk.BOTTOM, pady=10)
        self.ok_button = ttk.Button(
            self.button_area, text="OK"
        )
        self.cancel_button = ttk.Button(
            self.button_area, text="キャンセル", command=self.destroy
        )
        self.ok_button.pack(side=tk.LEFT, padx=5)
        self.cancel_button.pack(side=tk.LEFT, padx=5)

        # 選択領域の設定
        self.isu_area = ScrollableFrame(self)
        self.isu_area.pack(padx=10, pady=5)

        isu = InclusionSettingUnit(
            self.isu_area.interior, name_list=self.name_list
        )
        isu.add_button.bind(
            sequence="<ButtonPress>", func=self._add_isu
        )
        isu.destroy_button.bind(
            sequence="<ButtonPress>", func=self._destroy_isu
        )
        isu.one_unit()
        self.isu_list.append(isu)
        isu.pack(expand=True, fill=tk.X, pady=5)

        if custom_dict:
            self.read_custom_dict(custom_dict)

    def _add_isu(self, event=None):
        if event is None:
            id_ = len(self.isu_list)
        else:
            child_unit = self.nametowidget(event.widget.winfo_parent())
            unit = self.nametowidget(child_unit.winfo_parent())
            id_ = self.isu_list.index(unit)
            id_ += 1

        new_isu = InclusionSettingUnit(
            self.isu_area.interior, name_list=self.name_list
        )
        new_isu.add_button.bind(
            sequence="<ButtonPress>", func=self._add_isu
        )
        new_isu.destroy_button.bind(
            sequence="<ButtonPress>", func=self._destroy_isu
        )
        self.isu_list.insert(id_, new_isu)
        while id_ < len(self.isu_list):
            self.isu_list[id_].pack_forget()
            self.isu_list[id_].pack(expand=True, fill=tk.X, pady=5)
            id_ += 1
        self.isu_list[0].not_one_unit()

    def _destroy_isu(self, event=None):
        if event is not None:
            if event.widget["state"] != tk.DISABLED:
                child_unit = self.nametowidget(event.widget.winfo_parent())
                unit = self.nametowidget(child_unit.winfo_parent())
                id_ = self.isu_list.index(unit)
                del self.isu_list[id_]
                unit.destroy()
                if len(self.isu_list) == 1:
                    self.isu_list[0].one_unit()

    def read_custom_dict(self, custom_dict):
        for _ in range(1, len(custom_dict)):
            self._add_isu()

        for i, key in enumerate(custom_dict):
            self.isu_list[i].read_custom_name(list_=custom_dict[key], name=key)


class InclusionSettingUnit(tk.LabelFrame):
    def __init__(self, master=None, name_list=None):
        super().__init__(master)

        self.name_list = name_list
        self.inu_list = []

        # self.cbox = ttk.Combobox(self, values=self.name_list, state="readonly")
        # self.label = tk.Label(self, text="←(含める)─")
        self.inu_area = tk.Frame(self)

        # self.cbox.pack(side=tk.LEFT, anchor=tk.N)
        # self.cbox.bind("<<ComboboxSelected>>", self.set_same_name)
        # self.label.pack(side=tk.LEFT, anchor=tk.N)
        self.inu_area.pack(side=tk.LEFT)

        inu = IncludedNameUnit(self.inu_area, name_list=self.name_list)
        inu.add_button.bind(
            sequence="<ButtonPress>", func=self.add_inu
        )
        inu.destroy_button.bind(
            sequence="<ButtonPress>", func=self._destroy_inu
        )
        inu.first_unit(1)
        inu.cb.bind("<<ComboboxSelected>>", self._set_same_name)
        self.inu_list.append(inu)
        inu.pack(expand=True, fill=tk.X)

        self.label_unit = tk.Frame(self, bd=1, relief=tk.GROOVE)
        self.name_entry = ttk.Entry(self.label_unit)
        self.add_button = tk.Button(self.label_unit, text="+")
        self.destroy_button = tk.Button(self.label_unit, text="×")

        self.name_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.add_button.pack(side=tk.LEFT)
        self.destroy_button.pack(side=tk.LEFT)

        self.config(labelwidget=self.label_unit)

    def _set_same_name(self, event=None):
        current_name = self.name_entry.get()
        if not current_name or current_name in self.name_list:
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, self.inu_list[0].get())

    def one_unit(self):
        self.destroy_button.config(state=tk.DISABLED)

    def not_one_unit(self):
        self.destroy_button.config(state=tk.ACTIVE)

    def add_inu(self, event=None):
        if event is None:
            id_ = len(self.inu_list)
        else:
            unit = self.nametowidget(event.widget.winfo_parent())
            id_ = self.inu_list.index(unit)
            id_ += 1

        new_inu = IncludedNameUnit(self.inu_area, name_list=self.name_list)
        new_inu.add_button.bind(
            sequence="<ButtonPress>", func=self.add_inu
        )
        new_inu.destroy_button.bind(
            sequence="<ButtonPress>", func=self._destroy_inu
        )
        self.inu_list.insert(id_, new_inu)
        while id_ < len(self.inu_list):
            self.inu_list[id_].pack_forget()
            self.inu_list[id_].pack(expand=True, fill=tk.X)
            id_ += 1
        self.inu_list[0].first_unit(len(self.inu_list))

    def _destroy_inu(self, event=None):
        if event is not None:
            if event.widget["state"] != tk.DISABLED:
                unit = self.nametowidget(event.widget.winfo_parent())
                id = self.inu_list.index(unit)
                del self.inu_list[id]
                unit.destroy()
                self.inu_list[0].first_unit(len(self.inu_list))
                self.inu_list[0].cb.bind(
                    "<<ComboboxSelected>>", self._set_same_name
                )

    def get_name(self):
        if not self.name_entry.get():
            self._set_same_name()
        return self.name_entry.get()

    def read_custom_name(self, list_, name=None):
        for _ in range(1, len(list_)):
            self.add_inu()

        for i, member in enumerate(list_):
            self.inu_list[i].cb.set(member)

        if name:
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, name)


class IncludedNameUnit(tk.Frame):
    def __init__(self, master=None, name_list=None):
        super().__init__(master)

        self.label = tk.Label(self, text="            ")
        self.cb = ttk.Combobox(self, values=name_list, state="readonly")
        self.add_button = tk.Button(self, text="+")
        self.destroy_button = tk.Button(self, text="×")

        self.label.pack(side=tk.LEFT)
        self.cb.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.add_button.pack(side=tk.LEFT)
        self.destroy_button.pack(side=tk.LEFT)

    def first_unit(self, length):
        if length == 1:
            self.destroy_button.config(state=tk.DISABLED)
        else:
            self.destroy_button.config(state=tk.ACTIVE)

    def get(self):
        return self.cb.get()


if __name__ == "__main__":
    root = tk.Tk()

    # isu = InclusionSettingUnit(root, name_list=[i for i in "abcde"])
    # isu.pack()

    kari_name_list = [i for i in "abcde"]

    def activate_window():
        t = MemActsDetailSelectionToplevel(
            root, name_list=kari_name_list.copy()
        )

    button = tk.Button(root, text="展開", command=activate_window)
    button.pack(padx=20, pady=10)

    root.mainloop()
