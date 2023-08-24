import re
import tkinter as tk


class ValidateCommands(tk.Frame):
    """
    汎用的な入力規制に用いることのできる入力規制を定義するクラス

    for example:

    vcmd = ValidateCommands()

    entry = tk.Entry(root, validate="key", validatecommand=(vcmd.int, "%P"))

    """
    def __init__(self,
                 int_=False,
                 float_=False,
                 hex_=False,
                 date_=False,
                 date_slash=False,
                 date_hyphen=False,
                 filepath=False,
                 filename=False):
        """
        それぞれTrueにすることで入力規制に用いることができるtcl関数がregisterされる

        :param int_: 半角数字
        :param float_: 半角の整数・小数
        :param hex_: 半角の16進数(0~F,f)
        :param filepath: ファイルパスに使用できる文字
        :param filename: ファイル名に使用できる文字
        """
        super().__init__()
        if int_:
            self.int = self.register(self.val_integer)
        if float_:
            self.float = self.register(self.val_float)
        if hex_:
            self.hex = self.register(self.val_hexadecimal)
        if date_:
            self.date = self.register(self.val_date)
        if date_slash:
            self.date_slash = self.register(self.val_date_slash)
        if date_hyphen:
            self.date_hyphen = self.register(self.val_date_hyphen)
        if filepath:
            self.filepath = self.register(self.val_filepath)
        if filename:
            self.filename = self.register(self.val_filename)

    @staticmethod
    def val_integer(after=None):
        """
        半角数字と空白の場合のみTrueを返す入力規制
        """
        if re.fullmatch(re.compile("[0-9]*"), after):
            return True
        return False

    @staticmethod
    def val_float(after=None):
        """
        半角の整数・小数と空白の場合のみTrueを返す入力規制
        """
        if re.fullmatch(re.compile(r"[0-9]*\.?[0-9]*"), after):
            return True
        return False

    @staticmethod
    def val_hexadecimal(after=None):
        """
        半角の16進数(0~f)と空白の場合のみTrueを返す入力規制
        大文字・小文字両方可
        """
        if re.fullmatch(re.compile(r"[0-9a-fA-F]*"), after):
            return True
        return False

    def val_date(self, after=None):
        """
        入力後の値が半角日付(YYYY/MM/DD または YYYY-MM-DD)である場合にTrueを返す入力規制
        """
        if self.val_date_slash(after):
            return True
        if self.val_date_hyphen(after):
            return True
        return False

    @staticmethod
    def val_date_slash(after=None):
        """
        入力後の値が半角日付(YYYY/MM/DD)である場合のみTrueを返す入力規制
        """
        if re.fullmatch(re.compile(r"[0-9]{,4}/?[0-9]{,2}/?[0-9]{,2}"), after):
            return True
        return False

    @staticmethod
    def val_date_hyphen(after=None):
        """
        入力後の値が半角日付(YYYY-MM-DD)である場合のみTrueを返す入力規制
        """
        if re.fullmatch(re.compile(r"[0-9]{,4}-?[0-9]{,2}-?[0-9]{,2}"), after):
            return True
        return False

    @staticmethod
    def val_filepath(after=None):
        """
        ファイルパスに使用できる文字のみTrueを返す入力規制
        """
        if re.search(re.compile(r'[,|;|*|?|"|<|>|.|\|]'), after):
            return False
        return True

    @staticmethod
    def val_filename(after=None):
        """
        ファイル名に使用できる文字のみTrueを返す入力規制
        """
        if re.search(re.compile(r'[\\|/|:|,|;|*|?|"|<|>|.|\|]'), after):
            return False
        return True


# テスト用
if __name__ == "__main__":
    root = tk.Tk()

    vcmd = ValidateCommands(int_=True, float_=True)

    entry = tk.Entry(root, validate="key", validatecommand=(vcmd.float, "%P"))
    entry.pack(padx=30, pady=20)

    root.mainloop()
