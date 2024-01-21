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
from tkinter import ttk, messagebox, scrolledtext

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

        # 绑定单击事件
        self.tree.bind("<ButtonRelease-1>", self.on_tree_click)

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

    def on_tree_click(self, event):
        item_id = self.tree.identify_row(event.y)
        if item_id:
            # 获取点击的行的数据
            values = self.tree.item(item_id, "values")
            print("values:", values)
            ack = values[0]
            seq = values[1]
            curr_data = _data[int(ack)]
            paket_infos = curr_data["PKTs"]
            # 调用回调函数显示详情信息
            for pkt_info in paket_infos:
                if pkt_info["tcp_seq"] == int(seq):
                    app.show_detail_window(pkt_info)
                    break


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
        self.input_entry.insert(tk.END, "tcp and ip src 192.168.1.57")

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
            # messagebox.showinfo("SuperSniffer", f"filter: {filter_value}")
            self.sniffer = NetSniffer(filter_value)
            self.sniffer.start()
            self.input_entry.config(state=tk.DISABLED)

    def show_detail_window(self, values: dict):
        # 创建新窗口显示详细信息
        detail_window = tk.Toplevel(self.root)
        detail_window.title("Detail Window")
        detail_window.geometry("800x600")
        # 创建标签显示详细信息
        # for i, label_text in enumerate(
        #         ["TCP Ack", "TCP Seq", "IP src", "TCP sport", "IP dst", "TCP dport", "IP ttl", "Accept-Ranges", "Content-Type", "Content-Length", "Sever",
        #          "Content"]):
        #     tk.Label(detail_window, text=f"{label_text}:").grid(row=i, column=0, sticky=tk.E)
        #     tk.Label(detail_window, text=values[i]).grid(row=i, column=1, sticky=tk.W)
        for i, key in enumerate(values.keys()):
            if key == "load":
                pass
            else:
                tk.Label(detail_window, text=f"{key}:").grid(row=i, column=0, sticky=tk.E)
                tk.Label(detail_window, text=values[key]).grid(row=i, column=1, sticky=tk.W)
        # 创建滚动文本框
        load_row_index = len(values.keys()) + 1
        tk.Label(detail_window, text=f"Load:").grid(row=load_row_index, column=0, sticky=tk.E)
        textel = tk.scrolledtext.ScrolledText(detail_window, wrap=tk.WORD, width=40, height=10)
        textel.grid(row=load_row_index, column=1, sticky=tk.W)
        textel.insert(tk.END, values["load"])


if __name__ == "__main__":
    print(sys.argv)
    # 创建主窗口
    root = tk.Tk()
    root.geometry("1400x1400")
    app = App(root)

    # 运行主循环
    root.mainloop()
