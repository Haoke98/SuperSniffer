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
import random


class DataTable(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        self.table = ttk.Treeview(self, columns=["Name", "Age", "City"], show="headings")
        for column in ["Name", "Age", "City"]:
            self.table.heading(column, text=column)
            self.table.column(column, width=100)

        self.table.pack(expand=True, fill="both")

        # 初始数据
        self.update_data()

    def update_data(self):
        # 模拟更新数据，可以替换成你的数据更新逻辑
        updated_data = {
            "Name": ["Alice", "Bob", "Charlie"],
            "Age": [random.randint(20, 40) for _ in range(3)],
            "City": ["New York", "San Francisco", "Los Angeles"]
        }

        # 清空表格
        for item in self.table.get_children():
            self.table.delete(item)

        # 插入新数据
        for row in zip(updated_data["Name"], updated_data["Age"], updated_data["City"]):
            self.table.insert("", "end", values=row)

        # 每分钟调用一次更新数据函数
        self.after(1000, self.update_data)


if __name__ == "__main__":
    # 创建主窗口
    root = tk.Tk()
    root.title("Data Table Example")

    # 创建 DataTable 实例
    data_table = DataTable(root)
    data_table.pack(expand=True, fill="both")

    # 运行主循环
    root.mainloop()
