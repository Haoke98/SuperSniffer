# _*_ codign:utf8 _*_
"""====================================
@Author:Sadam·Sadik
@Email：1903249375@qq.com
@Date：2024/1/21
@Software: PyCharm
@disc:
======================================="""
import sys
import threading
import tkinter as tk
from tkinter import ttk, messagebox

from core import _columns, _data, NetSniffer


class DataTable(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        _column_index = list(_columns.keys())
        print(_column_index)
        self.tree = ttk.Treeview(self, columns=_column_index, show="tree")
        self.tree.heading("#0", text="HTTP请求/TCP请求包")
        for column in _columns.keys():
            self.tree.heading(column, text=column)
            columnInfo = _columns[column]
            self.tree.column(column, width=columnInfo["width"])

        # 初始数据
        self.update_data()

        self.tree.pack(expand=True, fill="both")

    def update_data(self):
        # 模拟更新数据，可以替换成你的数据更新逻辑

        # 清空树
        for item in self.tree.get_children():
            self.tree.delete(item)

        # 插入新数据
        for class_name, class_info in _data.items():
            pkts = class_info["PKTs"]
            class_node = self.tree.insert("", "end", text=class_name, values=(
                pkts.__len__(),
                class_info.get("Teacher", "")
            ), open=True)

            for student in pkts:
                _values = []
                for c in _columns.keys():
                    _values.append(student.get(c, ""))
                self.tree.insert(class_node, "end", values=_values)

        # 每分钟调用一次更新数据函数
        self.after(100, self.update_data)


class App:
    def __init__(self, root):
        self.sniffer = None
        self.root = root
        self.root.title("SuperSniffer")

        # 创建工具栏
        self.toolbar = tk.Frame(root)
        self.toolbar.pack(side=tk.TOP, fill=tk.X)

        # 创建开始/暂停按钮
        self.start_stop_button = tk.Button(self.toolbar, text="Start", command=self.toggle_update)
        self.start_stop_button.pack(side=tk.LEFT)

        # 创建输入框
        self.input_entry = tk.Entry(self.toolbar)
        self.input_entry.pack(side=tk.LEFT)

        # 创建 DataTable 实例，并传递工具栏
        self.data_table = DataTable(root)
        self.data_table.pack(expand=True, fill="both")

        # 初始化定时器状态
        self.is_update_running = True
        self.toggle_update()

    def toggle_update(self):
        # 切换开始/暂停按钮状态
        if self.is_update_running:
            self.start_stop_button.config(text="Start")
            self.is_update_running = False
            # 执行 结束
            if self.sniffer:
                self.sniffer.stop()
        else:
            self.start_stop_button.config(text="Stop")
            self.is_update_running = True
            # 启动或重新启动数据更新定时器
            self.data_table.update_data()
            # 执行 开始
            filter_value = self.input_entry.get()
            messagebox.showinfo("SuperSniffer", f"filter: {filter_value}")
            self.sniffer = NetSniffer(filter_value)
            self.sniffer.start()
            self.input_entry.config(state=tk.DISABLED)


if __name__ == "__main__":
    print(sys.argv)
    # 创建主窗口
    root = tk.Tk()
    app = App(root)

    # 运行主循环
    root.mainloop()
