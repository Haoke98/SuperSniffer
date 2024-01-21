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

        self.tree = ttk.Treeview(self, columns=["Name", "Age", "City"], show="tree")
        self.tree.heading("#0", text="Class")
        for column in ["Name", "Age", "City"]:
            self.tree.heading(column, text=column)
            self.tree.column(column, width=100)

        # 初始数据
        self.update_data()

        self.tree.pack(expand=True, fill="both")

    def update_data(self):
        # 模拟更新数据，可以替换成你的数据更新逻辑
        class_data = {
            "Class A": {
                "Students": [
                    {"Name": "Alice", "Age": random.randint(20, 40), "City": "New York"},
                    {"Name": "Bob", "Age": random.randint(20, 40), "City": "San Francisco"}
                ]
            },
            "Class B": {
                "Students": [
                    {"Name": "Charlie", "Age": random.randint(20, 40), "City": "Los Angeles"},
                    {"Name": "David", "Age": random.randint(20, 40), "City": "Chicago"}
                ]
            }
        }

        # 清空树
        for item in self.tree.get_children():
            self.tree.delete(item)

        # 插入新数据
        for class_name, class_info in class_data.items():
            class_node = self.tree.insert("", "end", text=class_name)

            for student in class_info["Students"]:
                self.tree.insert(class_node, "end", values=(student["Name"], student["Age"], student["City"]))

        # 每分钟调用一次更新数据函数
        self.after(60000, self.update_data)


if __name__ == "__main__":
    # 创建主窗口
    root = tk.Tk()
    root.title("Tree Table Example")

    # 创建 DataTable 实例
    data_table = DataTable(root)
    data_table.pack(expand=True, fill="both")

    # 运行主循环
    root.mainloop()
