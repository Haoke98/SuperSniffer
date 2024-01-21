# _*_ codign:utf8 _*_
"""====================================
@Author:Sadam·Sadik
@Email：1903249375@qq.com
@Date：2024/1/21
@Software: PyCharm
@disc:
======================================="""
import tkinter as tk
from tkinter import ttk


class DataTable(tk.Frame):
    def __init__(self, parent, data):
        super().__init__(parent)
        self.parent = parent
        self.data = data

        self.table = ttk.Treeview(self, columns=list(data.keys()), show="headings")
        for column in data.keys():
            self.table.heading(column, text=column)
            self.table.column(column, width=100)  # 设置列宽度

        for row in data.values():
            self.table.insert("", "end", values=row)

        self.table.pack(expand=True, fill="both")


if __name__ == "__main__":
    # 示例数据
    sample_data = {
        "Name": ["Alice", "Bob", "Charlie"],
        "Age": [25, 30, 22],
        "City": ["New York", "San Francisco", "Los Angeles"]
    }

    # 创建主窗口
    root = tk.Tk()
    root.title("Data Table Example")

    # 创建 DataTable 实例
    data_table = DataTable(root, sample_data)
    data_table.pack(expand=True, fill="both")

    # 运行主循环
    root.mainloop()
